from decimal import Decimal
import random
from django.db import transaction, connection
from django.db.models import F
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Profile
from .models import Prize, CaseType, Case, CasePrize, Spin, BonusSpin
from accounts.serializers import ProfileSerializer
from .serializers import (
    PrizeSerializer, CaseTypeSerializer, CaseSerializer, CaseDetailSerializer,
    CasePrizeSerializer, SpinSerializer, SpinListSerializer, BonusSpinSerializer
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

    def _has_parent_spin_field(self):
        """Проверяет, существует ли поле parent_spin в таблице"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM cases_spin LIKE 'parent_spin_id'")
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def _open_case_once(self, case, prof, user, server_seed, client_seed, base_nonce, nonce_offset=0, is_bonus_open=False, parent_spin=None):
        """
        Вспомогательная функция для открытия кейса один раз.
        Возвращает (spin_or_bonus_spin, amount, bonus_info)
        bonus_info = {"has_bonus": bool, "bonus_type": str, "bonus_multiplier": int, "bonus_rng": Decimal}
        """
        prizes = list(case.prizes.all())
        if not prizes:
            return None, Decimal("0.0"), {"has_bonus": False}

        # Используем nonce с offset для provably fair
        current_nonce = base_nonce + nonce_offset
        msg = f"{client_seed}:{current_nonce}"
        digest_hex = hmac_sha256_hex(server_seed, msg)
        r = digest_to_uniform(digest_hex)

        # Снимок весов на момент спина
        weights_snapshot = [
            {
                "case_prize_id": p.id, 
                "prize_id": p.id,
                "weight": int(max(1, p.weight or 1)), 
                "amount_min_usd": str(p.amount_min_usd),
                "amount_max_usd": str(p.amount_max_usd),
                "amount_usd": str(p.amount_min_usd),
                "prize_name": p.prize.name if p.prize else p.prize_name
            }
            for p in prizes
        ]

        # Детерминированный выбор приза
        case_prize = pick_by_weights(r, [{"obj": p, "weight": p.weight} for p in prizes])
        
        # Генерируем случайную сумму в диапазоне
        base_amount = case_prize.get_random_amount()

        # Проверяем бонус (только для основного открытия, не для доп. открытий)
        bonus_info = {"has_bonus": False}
        if not is_bonus_open and case.bonus_chance and case.bonus_chance > 0:
            # Используем следующий nonce для проверки бонуса
            bonus_nonce = current_nonce + 1
            bonus_msg = f"{client_seed}:{bonus_nonce}"
            bonus_digest = hmac_sha256_hex(server_seed, bonus_msg)
            bonus_r = digest_to_uniform(bonus_digest)
            
            if bonus_r < Decimal(str(case.bonus_chance)):
                bonus_info["has_bonus"] = True
                bonus_info["bonus_rng"] = bonus_r
                
                # Определяем тип бонуса
                type_nonce = bonus_nonce + 1
                type_msg = f"{client_seed}:{type_nonce}"
                type_digest = hmac_sha256_hex(server_seed, type_msg)
                type_r = digest_to_uniform(type_digest)
                
                if type_r < Decimal(str(case.bonus_type_chance_multiplier or 0.5)):
                    # Множитель
                    bonus_info["bonus_type"] = "multiplier"
                    multipliers = case.bonus_multipliers or []
                    if multipliers:
                        # Выбираем множитель по весам
                        # Используем следующий nonce для выбора множителя
                        mult_nonce = type_nonce + 1
                        mult_msg = f"{client_seed}:{mult_nonce}"
                        mult_digest = hmac_sha256_hex(server_seed, mult_msg)
                        mult_r = digest_to_uniform(mult_digest)
                        
                        multiplier_items = [{"obj": m, "weight": m.get("weight", 1)} for m in multipliers]
                        selected_mult = pick_by_weights(mult_r, multiplier_items)
                        bonus_info["bonus_multiplier"] = selected_mult.get("multiplier", 2)
                    else:
                        bonus_info["bonus_multiplier"] = 2  # По умолчанию x2
                else:
                    # Дополнительное открытие
                    bonus_info["bonus_type"] = "extra_open"

        # Создаем спин или бонус-спин
        if is_bonus_open and parent_spin:
            # Создаем BonusSpin для дополнительного открытия
            bonus_spin = BonusSpin.objects.create(
                parent_spin=parent_spin,
                case=case,
                case_prize=case_prize,
                user=user,
                actual_amount_usd=base_amount,
                server_seed_hash=sha256_hex(server_seed),
                server_seed=server_seed,
                client_seed=client_seed,
                nonce=current_nonce,
                roll_digest=digest_hex,
                rng_value=r,
                weights_snapshot=weights_snapshot,
            )
            return bonus_spin, base_amount, bonus_info
        else:
            # Создаем обычный Spin
            spin = Spin.objects.create(
                case=case,
                case_prize=case_prize,
                user=user,
                actual_amount_usd=base_amount,
                base_amount_usd=base_amount,
                server_seed_hash=sha256_hex(server_seed),
                server_seed=server_seed,
                client_seed=client_seed,
                nonce=current_nonce,
                roll_digest=digest_hex,
                rng_value=r,
                weights_snapshot=weights_snapshot,
                has_bonus=bonus_info.get("has_bonus", False),
                bonus_type=bonus_info.get("bonus_type"),
                bonus_multiplier=bonus_info.get("bonus_multiplier"),
            )
            return spin, base_amount, bonus_info

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
            base_nonce = prof.next_nonce()  # атомарно +1 под блокировкой профиля

            server_seed = generate_server_seed()
            server_hash = sha256_hex(server_seed)

            # ====== Основное открытие кейса ======
            main_spin, base_amount, bonus_info = self._open_case_once(
                case, prof, request.user, server_seed, client_seed, base_nonce, nonce_offset=0, is_bonus_open=False
            )

            if not main_spin:
                return Response({"detail": "Ошибка при открытии кейса"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Обновляем PF данные для основного спина (если они еще не установлены)
            if not main_spin.server_seed_hash:
                main_spin.server_seed_hash = server_hash
                main_spin.server_seed = server_seed
                main_spin.client_seed = client_seed
                main_spin.nonce = base_nonce
                msg = f"{client_seed}:{base_nonce}"
                main_spin.roll_digest = hmac_sha256_hex(server_seed, msg)
                main_spin.rng_value = digest_to_uniform(main_spin.roll_digest)

            total_amount = base_amount
            bonus_spins_data = []

            # ====== Обработка бонуса ======
            if bonus_info.get("has_bonus"):
                main_spin.has_bonus = True
                main_spin.bonus_type = bonus_info.get("bonus_type")
                main_spin.base_amount_usd = base_amount

                if bonus_info.get("bonus_type") == "multiplier":
                    # Применяем множитель
                    multiplier = bonus_info.get("bonus_multiplier", 2)
                    main_spin.bonus_multiplier = multiplier
                    total_amount = base_amount * Decimal(multiplier)
                    main_spin.actual_amount_usd = total_amount

                elif bonus_info.get("bonus_type") == "extra_open":
                    # Дополнительные открытия - создаем BonusSpin записи
                    max_opens = case.max_bonus_opens or 1
                    opens_done = 0
                    nonce_offset = 2  # Начинаем с offset 2 (0 - основной, 1 - проверка бонуса, 2+ - доп. открытия)

                    while opens_done < max_opens:
                        bonus_spin_obj, bonus_amount, _ = self._open_case_once(
                            case, prof, request.user, server_seed, client_seed, base_nonce,
                            nonce_offset=nonce_offset, is_bonus_open=True, parent_spin=main_spin
                        )
                        if bonus_spin_obj:
                            total_amount += bonus_amount
                            # Сохраняем полную информацию о дополнительном спине для PF
                            bonus_spins_data.append({
                                "bonus_spin_id": bonus_spin_obj.id,
                                "amount": str(bonus_amount),
                                "bonus_type": None,  # Доп. открытия не имеют своих бонусов
                                "is_extra_open": True,  # Флаг что это дополнительное открытие
                                "nonce": bonus_spin_obj.nonce,  # Для PF верификации
                            })
                            opens_done += 1
                            nonce_offset += 1
                        else:
                            break

                    main_spin.actual_amount_usd = total_amount
                    main_spin.bonus_spins = bonus_spins_data

            # ====== Денежная логика ======
            prof.balance_usd -= price
            prof.balance_usd += total_amount

            net = total_amount - price
            if net >= 0:
                prof.won_total_usd += net
            else:
                prof.lost_total_usd += -net

            if case.is_limited_mode():
                Case.objects.filter(pk=case.pk).update(spins_used=F("spins_used") + 1)
                case.refresh_from_db(fields=["spins_used"])

            prof.save(update_fields=["balance_usd", "won_total_usd", "lost_total_usd", "pf_nonce", "updated_at"])
            main_spin.save()

            data = {
                "case": CaseSerializer(case, context=self.get_serializer_context()).data,
                "spin": SpinSerializer(main_spin, context=self.get_serializer_context()).data,
                "profile": ProfileSerializer(prof).data,
                # Дополнительно — быстрое поле для фронта:
                "provably_fair": {
                    "serverSeedHash": server_hash,
                    "serverSeed": server_seed,
                    "clientSeed": client_seed,
                    "nonce": base_nonce,
                    "rollDigest": main_spin.roll_digest,
                    "rngValue": str(main_spin.rng_value),
                    "amount_usd": str(total_amount),
                    "base_amount_usd": str(base_amount),
                },
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
class SpinViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin , viewsets.GenericViewSet):
    queryset = Spin.objects.select_related("case", "prize")
    serializer_class = SpinSerializer
    permission_classes = [permissions.IsAuthenticated]  # историю и проверку — только владельцу? иначе AllowAny
    
    pagination_class = SmallPages

    def _has_parent_spin_field(self):
        """Проверяет, существует ли поле parent_spin в таблице"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM cases_spin LIKE 'parent_spin_id'")
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def get_queryset(self):
        qs = Spin.objects.select_related("case", "prize").prefetch_related("bonus_spin_records")
        # Для публичной проверки PF не ограничиваем пользователя
        if getattr(self, "action", None) == "verify":
            return qs
        # Показываем все крутки (дополнительные открытия теперь в отдельной таблице BonusSpin)
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

    # /api/spins/my/ — явный эндпоинт "мои спины" (эквивалент list для обычного юзера)
    @action(detail=False, methods=["get"], url_path="my", permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        qs = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page, many=True)
        return self.get_paginated_response(ser.data)
    
    # /api/spins/history/ — объединенная история спинов и бонусных спинов
    @action(detail=False, methods=["get"], url_path="history", permission_classes=[permissions.IsAuthenticated])
    def history(self, request):
        """Объединенная история всех спинов (обычных и бонусных)"""
        user = request.user
        
        # Получаем обычные спины
        spins_qs = Spin.objects.filter(user=user).select_related("case", "prize").prefetch_related("bonus_spin_records")
        
        # Получаем бонусные спины
        bonus_spins_qs = BonusSpin.objects.filter(user=user).select_related("parent_spin", "case", "case_prize")
        
        # Объединяем и сортируем по дате
        from itertools import chain
        from operator import attrgetter
        
        all_items = list(chain(spins_qs, bonus_spins_qs))
        all_items.sort(key=attrgetter('created_at'), reverse=True)
        
        # Пагинация
        page = self.paginate_queryset(all_items)
        if page is not None:
            # Сериализуем каждый элемент в зависимости от типа
            results = []
            for item in page:
                if isinstance(item, Spin):
                    results.append(SpinListSerializer(item, context=self.get_serializer_context()).data)
                elif isinstance(item, BonusSpin):
                    # Преобразуем BonusSpin в формат, похожий на SpinListSerializer
                    results.append({
                        "id": item.id,
                        "created_at": item.created_at,
                        "case_id": item.case_id,
                        "case_name": item.case.name,
                        "prize_title": item.case_prize.prize.name if item.case_prize and item.case_prize.prize else None,
                        "amount_usd": str(item.actual_amount_usd),
                        "parent_spin_id": item.parent_spin_id,
                        "is_extra_open": True,
                        "is_bonus_spin": True,  # Флаг что это BonusSpin
                    })
            return self.get_paginated_response(results)
        
        # Если пагинация не используется
        results = []
        for item in all_items:
            if isinstance(item, Spin):
                results.append(SpinListSerializer(item, context=self.get_serializer_context()).data)
            elif isinstance(item, BonusSpin):
                results.append({
                    "id": item.id,
                    "created_at": item.created_at,
                    "case_id": item.case_id,
                    "case_name": item.case.name,
                    "prize_title": item.case_prize.prize.name if item.case_prize and item.case_prize.prize else None,
                    "amount_usd": str(item.actual_amount_usd),
                    "parent_spin_id": item.parent_spin_id,
                    "is_extra_open": True,
                    "is_bonus_spin": True,
                })
        return Response({"results": results, "count": len(results)})

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
            # Поддерживаем как старый формат (prize_id), так и новый (case_prize_id)
            prize_id = item.get("case_prize_id") or item.get("prize_id")
            p = prizes_by_id.get(prize_id)
            if p:
                items.append({"obj": p, "weight": int(item.get("weight", 1))})
        if not items:
            # fallback — текущее состояние (не идеально, но лучше чем ничего)
            items = [{"obj": p, "weight": p.weight} for p in spin.case.prizes.all()]

        recomputed_prize = pick_by_weights(rng, items)
        
        # Проверяем соответствие приза (поддерживаем старые и новые спины)
        actual_prize_id = spin.case_prize_id if spin.case_prize_id else spin.prize_id
        prize_matches = (recomputed_prize.id == actual_prize_id)

        return Response({
            "ok": bool(ok_hash and digest_hex == spin.roll_digest and prize_matches),
            "checks": {
                "serverSeedHashMatches": ok_hash,
                "rollDigestMatches": (digest_hex == spin.roll_digest),
                "prizeMatches": prize_matches,
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
                "prize_id": actual_prize_id,
            }
        })


class BonusSpinViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ViewSet для дополнительных открытий"""
    queryset = BonusSpin.objects.select_related("parent_spin", "case", "case_prize")
    serializer_class = BonusSpinSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        qs = BonusSpin.objects.select_related("parent_spin", "case", "case_prize")
        user = self.request.user
        if user and user.is_staff:
            return qs
        return qs.filter(user=user)


class PrizeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления призами"""
    queryset = Prize.objects.all()
    serializer_class = PrizeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Для обычных пользователей показываем только активные призы
        if not self.request.user.is_staff:
            return Prize.objects.filter(is_active=True)
        return Prize.objects.all()