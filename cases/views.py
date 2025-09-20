from decimal import Decimal
import random
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Profile
from .models import CaseType, Case, CasePrize, Spin
from accounts.serializers import ProfileSerializer
from .serializers import (
    CaseTypeSerializer, CaseSerializer, CaseDetailSerializer,
    CasePrizeSerializer, SpinSerializer, SpinListSerializer
)
from .pf_utils import (
    generate_server_seed, sha256_hex, hmac_sha256_hex, digest_to_uniform, pick_by_weights
)
from rest_framework import mixins

from rest_framework.pagination import PageNumberPagination

class SmallPages(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100



class CaseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CaseType.objects.filter(is_active=True)
    serializer_class = CaseTypeSerializer
    permission_classes = [permissions.AllowAny]

class CaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Case.objects.all().select_related("type").prefetch_related("prizes")
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return CaseDetailSerializer if self.action == "retrieve" else CaseSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # фильтр по доступности (по умолчанию — только доступные)
        if not self.request.query_params.get("all"):
            qs = qs.available_now()

        # фильтр по типу: ?type=slug   или   ?type_id=1
        type = self.request.query_params.get("type")
        type_id = self.request.query_params.get("type_id")
        if type:
            qs = qs.filter(type__slug=type)
        if type_id:
            qs = qs.filter(type_id=type_id)
        return qs

    @action(detail=True, methods=["get"], url_path="prizes", permission_classes=[permissions.AllowAny])
    def prizes(self, request, pk=None):
        case = self.get_object()
        return Response(CasePrizeSerializer(case.prizes.all(), many=True).data)

    @action(detail=True, methods=["post"], url_path="spin", permission_classes=[permissions.IsAuthenticated])
    def spin(self, request, pk=None):
        with transaction.atomic():
            prof, _ = Profile.objects.select_for_update().get_or_create(user=request.user)
            case = Case.objects.select_for_update().get(pk=pk)

            if not case.is_active:
                return Response({"detail": "Кейс не активен"}, status=status.HTTP_400_BAD_REQUEST)
            if case.is_timed_mode() and not case.is_available_now():
                return Response({"detail": "Кейс вне окна доступности"}, status=status.HTTP_400_BAD_REQUEST)
            if case.is_limited_mode() and case.spins_remaining <= 0:
                return Response({"detail": "Лимит круток исчерпан"}, status=status.HTTP_400_BAD_REQUEST)

            price = Decimal(case.price_usd)
            if prof.balance_usd < price:
                return Response({"detail": "Недостаточно средств"}, status=status.HTTP_400_BAD_REQUEST)

            prizes = list(case.prizes.all())
            if not prizes:
                return Response({"detail": "У кейса нет призов"}, status=status.HTTP_400_BAD_REQUEST)

            # ====== PF: подготовка ======
            client_seed = prof.client_seed
            nonce = prof.next_nonce()  # атомарно +1 под блокировкой профиля

            server_seed = generate_server_seed()
            server_hash = sha256_hex(server_seed)

            msg = f"{client_seed}:{nonce}"
            digest_hex = hmac_sha256_hex(server_seed, msg)
            r = digest_to_uniform(digest_hex)

            # Снимок весов на момент спина
            weights_snapshot = [
                {"prize_id": p.id, "weight": int(max(1, p.weight or 1)), "amount_usd": str(p.amount_usd)}
                for p in prizes
            ]

            # Детерминированный выбор приза
            prize = pick_by_weights(r, [{"obj": p, "weight": p.weight} for p in prizes])

            # ====== Денежная логика (как у тебя) ======
            prof.balance_usd -= price
            prof.balance_usd += Decimal(prize.amount_usd)

            net = Decimal(prize.amount_usd) - price
            if net >= 0:
                prof.won_total_usd  += net
            else:
                prof.lost_total_usd += -net

            if case.is_limited_mode():
                Case.objects.filter(pk=case.pk).update(spins_used=F("spins_used") + 1)
                case.refresh_from_db(fields=["spins_used"])

            prof.save(update_fields=["balance_usd", "won_total_usd", "lost_total_usd", "pf_nonce", "updated_at"])

            # ====== Сохраняем PF-артефакты в Spin ======
            spin = Spin.objects.create(
                case=case,
                prize=prize,
                user=request.user,
                server_seed_hash=server_hash,
                server_seed=server_seed,         # ты можешь НЕ отдавать его сразу во фронт — решай бизнес-правилом
                client_seed=client_seed,
                nonce=nonce,
                roll_digest=digest_hex,
                rng_value=r,                     # Decimal хранится точно
                weights_snapshot=weights_snapshot,
            )

            data = {
                "case": CaseSerializer(case, context=self.get_serializer_context()).data,
                "spin": SpinSerializer(spin, context=self.get_serializer_context()).data,
                "profile": ProfileSerializer(prof).data,
                # Дополнительно — быстрое поле для фронта:
                "provably_fair": {
                    "serverSeedHash": server_hash,
                    "serverSeed": server_seed,   # если хочешь раскрывать сразу — оставить; иначе — убери
                    "clientSeed": client_seed,
                    "nonce": nonce,
                    "rollDigest": digest_hex,
                    "rngValue": str(r),
                },
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
class SpinViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin , viewsets.GenericViewSet):
    queryset = Spin.objects.select_related("case", "prize")
    serializer_class = SpinSerializer
    permission_classes = [permissions.IsAuthenticated]  # историю и проверку — только владельцу? иначе AllowAny
    
    pagination_class = SmallPages

    def get_queryset(self):
        qs = Spin.objects.select_related("case", "prize")
        # Для публичной проверки PF не ограничиваем пользователя
        if getattr(self, "action", None) == "verify":
            return qs
        # Админ видит все (с опц. фильтрами), обычный пользователь — только свои
        user = self.request.user
        if user and user.is_staff:
            user_id = self.request.query_params.get("user_id")
            case_id = self.request.query_params.get("case_id")
            if user_id:
                qs = qs.filter(user_id=user_id)
            if case_id:
                qs = qs.filter(case_id=case_id)
            return qs.order_by("-created_at")
        return qs.filter(user=user).order_by("-created_at")

    def get_serializer_class(self):
        # Для списков — лёгкий сериалайзер; для retrieve — полный
        if self.action in ("list", "my"):
            return SpinListSerializer
        return SpinSerializer

    # /api/spins/my/ — явный эндпоинт “мои спины” (эквивалент list для обычного юзера)
    @action(detail=False, methods=["get"], url_path="my", permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response(ser.data)

    @action(detail=True, methods=["get"], url_path="verify", permission_classes=[permissions.AllowAny])
    def verify(self, request, pk=None):
        spin = self.get_object()

        # 1) проверка коммита
        calculated_hash = sha256_hex(spin.server_seed)
        ok_hash = (calculated_hash == spin.server_seed_hash)

        # 2) пересчёт HMAC и rng
        msg = f"{spin.client_seed}:{spin.nonce}"
        digest_hex = hmac_sha256_hex(spin.server_seed, msg)
        rng = digest_to_uniform(digest_hex)

        # 3) выбор приза по snapshot весов
        # (берём призы по id из case.prizes, но веса — из snapshot)
        prizes_by_id = {p.id: p for p in spin.case.prizes.all()}
        items = []
        for item in (spin.weights_snapshot or []):
            p = prizes_by_id.get(item["prize_id"])
            if p:
                items.append({"obj": p, "weight": int(item.get("weight", 1))})
        if not items:
            # fallback — текущее состояние (не идеально, но лучше чем ничего)
            items = [{"obj": p, "weight": p.weight} for p in spin.case.prizes.all()]

        recomputed_prize = pick_by_weights(rng, items)

        return Response({
            "ok": bool(ok_hash and digest_hex == spin.roll_digest and recomputed_prize.id == spin.prize_id),
            "checks": {
                "serverSeedHashMatches": ok_hash,
                "rollDigestMatches": (digest_hex == spin.roll_digest),
                "prizeMatches": (recomputed_prize.id == spin.prize_id),
            },
            "recomputed": {
                "serverSeedHash": calculated_hash,
                "rollDigest": digest_hex,
                "rngValue": str(rng),
                "prize_id": recomputed_prize.id,
            },
            "original": {
                "serverSeedHash": spin.server_seed_hash,
                "rollDigest": spin.roll_digest,
                "rngValue": str(spin.rng_value),
                "prize_id": spin.prize_id,
            }
        })