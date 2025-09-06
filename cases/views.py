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
    CasePrizeSerializer, SpinSerializer
)

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
            # блокируем профиль и кейс, чтобы избежать гонок
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

            # списываем цену
            prof.balance_usd -= price

            # выбираем приз по весам
            weights = [max(1, p.weight or 1) for p in prizes]
            prize = random.choices(prizes, weights=weights, k=1)[0]

            # начисляем приз
            prof.balance_usd += Decimal(prize.amount_usd)

            # учёт выигрыша/проигрыша (net = prize - price)
            net = Decimal(prize.amount_usd) - price
            if net >= 0:
                prof.won_total_usd  += net
            else:
                prof.lost_total_usd += -net

            # уменьшаем лимит для лимитных
            if case.is_limited_mode():
                Case.objects.filter(pk=case.pk).update(spins_used=F("spins_used") + 1)
                case.refresh_from_db(fields=["spins_used"])

            prof.save(update_fields=["balance_usd", "won_total_usd", "lost_total_usd", "updated_at"])

            spin = Spin.objects.create(case=case, prize=prize, user=request.user)
            data = {
                "case": CaseSerializer(case, context=self.get_serializer_context()).data,
                "spin": SpinSerializer(spin, context=self.get_serializer_context()).data,
                "profile": ProfileSerializer(prof).data,
            }
            return Response(data, status=status.HTTP_201_CREATED)
