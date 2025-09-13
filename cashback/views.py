# cashback/views.py
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .models import CashbackAccrual, CashbackDebit
from accounts.models import Profile  # профиль с balance_usd

class MyCashbackListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = CashbackAccrual.objects.filter(user=request.user).order_by("-slot_started_at")[:200]
        items = [{
            "amount_usd": str(x.amount_usd),
            "slot_started_at": x.slot_started_at,
            "computed_at": x.computed_at,
            "status": x.status,
        } for x in qs]
        return Response({"items": items})


class MyCashbackSummaryView(APIView):
    """
    Возвращает:
      - total_accrued_usd: сумма начислений (не отменённых)
      - total_debited_usd: сумма списаний (не отменённых)
      - balance_usd: доступный кэшбэк = accrued - debited
      - last_items: последние операции (начисления и списания)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        accrued = (
            CashbackAccrual.objects
            .filter(user=u)
            .exclude(status=CashbackAccrual.STATUS_CANCELLED)
            .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00")
        )
        debited = (
            CashbackDebit.objects
            .filter(user=u)
            .exclude(status=CashbackDebit.STATUS_CANCELLED)
            .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00")
        )
        balance = (accrued - debited).quantize(Decimal("0.01"))

        # последние операции (по 10 + 10)
        last_acc = list(
            CashbackAccrual.objects.filter(user=u).order_by("-computed_at")[:10]
            .values("amount_usd", "computed_at", "status", "slot_started_at")
        )
        last_deb = list(
            CashbackDebit.objects.filter(user=u).order_by("-created_at")[:10]
            .values("amount_usd", "created_at", "status", "note")
        )
        return Response({
            "total_accrued_usd": str(accrued),
            "total_debited_usd": str(debited),
            "balance_usd": str(balance),
            "last_accruals": last_acc,
            "last_debits": last_deb,
        })


class MyCashbackClaimView(APIView):
    """
    Списать часть/весь кэшбэк на баланс профиля (в USD-эквиваленте).
    body: { "amount_usd": "25.00" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            amt = Decimal(str(request.data.get("amount_usd")))
        except Exception:
            return Response({"detail": "Некорректная сумма"}, status=status.HTTP_400_BAD_REQUEST)

        if amt <= 0:
            return Response({"detail": "Сумма должна быть > 0"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            u = request.user

            # Посчитаем доступный баланс кэшбэка
            accrued = (
                CashbackAccrual.objects
                .select_for_update()  # блокируем на время списания
                .filter(user=u)
                .exclude(status=CashbackAccrual.STATUS_CANCELLED)
                .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00")
            )
            debited = (
                CashbackDebit.objects
                .select_for_update()
                .filter(user=u)
                .exclude(status=CashbackDebit.STATUS_CANCELLED)
                .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00")
            )
            balance = (accrued - debited).quantize(Decimal("0.01"))
            if amt > balance:
                return Response({"detail": "Недостаточно доступного кэшбэка", "balance_usd": str(balance)},
                                status=status.HTTP_400_BAD_REQUEST)

            # Зачисляем на баланс пользователя (USD)
            prof, _ = Profile.objects.select_for_update().get_or_create(user=u)
            prof.balance_usd = (prof.balance_usd or Decimal("0.00")) + amt
            prof.save(update_fields=["balance_usd", "updated_at"])

            # Фиксируем списание кэшбэка
            debit = CashbackDebit.objects.create(
                user=u,
                amount_usd=amt,
                status=CashbackDebit.STATUS_COMPLETED,
                note="Перевод с кэшбэка на баланс",
            )

        return Response({
            "detail": "Кэшбэк зачислен на баланс",
            "debited": str(amt),
            "balance_usd": str((balance - amt).quantize(Decimal("0.01"))),
            "profile_balance_usd": str(prof.balance_usd),
            "debit_id": debit.id,
        }, status=status.HTTP_201_CREATED)
