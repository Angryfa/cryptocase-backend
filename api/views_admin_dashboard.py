# api/views_admin_dashboard.py
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from cases.models import Case, CaseType, CasePrize, Spin
from referrals.models import ReferralProfile
from accounts.models import Profile  # если нужно
# Если у тебя Withdrawal/Deposit лежат в другом приложении — поправь импорт:
from accounts.models import Withdrawal, Deposit  # у тебя такие модели есть в админке
# from payments.models import Withdrawal, Deposit  # если вдруг у тебя так

User = get_user_model()


class IsAdmin(permissions.IsAdminUser):
    pass


def _parse_period(request) -> Tuple[datetime, datetime]:
    """
    Поддерживаем:
      - ?preset=today|yesterday|7d|30d|this_month|prev_month
      - ?from=ISO8601&to=ISO8601 (кастомный период)
    Значения возвращаем timezone-aware (UTC).
    """
    tz = timezone.get_current_timezone()

    preset = (request.query_params.get("preset") or "").lower().strip()
    s_from = request.query_params.get("from")
    s_to   = request.query_params.get("to")

    now = timezone.now()
    today = now.astimezone(tz).date()

    if s_from or s_to:
        try:
            # DRF сам парсит ISO, но на всякий — делаем вручную
            dt_from = timezone.make_aware(datetime.fromisoformat(s_from)) if s_from else timezone.make_aware(datetime.combine(today, datetime.min.time()))
            dt_to   = timezone.make_aware(datetime.fromisoformat(s_to))   if s_to   else now
            return dt_from, dt_to
        except Exception:
            # fallback на 7 дней
            return now - timedelta(days=7), now

    if preset == "today":
        start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end   = now
        return start, end
    if preset == "yesterday":
        y = today - timedelta(days=1)
        return timezone.make_aware(datetime.combine(y, datetime.min.time())), timezone.make_aware(datetime.combine(y, datetime.max.time()))
    if preset in ("7d", "week"):
        return now - timedelta(days=7), now
    if preset in ("30d", "month"):
        return now - timedelta(days=30), now
    if preset == "this_month":
        start = timezone.make_aware(datetime.combine(today.replace(day=1), datetime.min.time()))
        return start, now
    if preset == "prev_month":
        first_this = today.replace(day=1)
        last_prev = first_this - timedelta(days=1)
        start = timezone.make_aware(datetime.combine(last_prev.replace(day=1), datetime.min.time()))
        end   = timezone.make_aware(datetime.combine(last_prev, datetime.max.time()))
        return start, end

    # по умолчанию 7 дней
    return now - timedelta(days=7), now


class AdminDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        dt_from, dt_to = _parse_period(request)

       # ===== 1) Прибыль платформы =====
        completed_codes = ("done", "approved", "completed", "paid", "success")

        dep_q = Deposit.objects.filter(created_at__gte=dt_from, created_at__lte=dt_to)
        dep_q_completed = dep_q.filter(status__code__in=completed_codes) if hasattr(Deposit, "status") else dep_q
        deposits_sum = dep_q_completed.aggregate(s=Sum("amount_usd"))["s"] or Decimal("0")

        spin_q = Spin.objects.filter(created_at__gte=dt_from, created_at__lte=dt_to)

        spins_count = spin_q.count()

        wins_q = spin_q.annotate(diff=F("prize__amount_usd") - F("case__price_usd")).filter(diff__gt=0)
        losses_q = spin_q.annotate(diff=F("case__price_usd") - F("prize__amount_usd")).filter(diff__gt=0)

        wins_sum   = wins_q.aggregate(s=Sum("diff"))["s"] or Decimal("0")
        losses_sum = losses_q.aggregate(s=Sum("diff"))["s"] or Decimal("0")

        profit_usd = deposits_sum + losses_sum - wins_sum

        # ===== 2) Прокрутки по типам кейсов =====
        spins_by_type = (
            spin_q
            .values("case__type_id", "case__type__name", "case__type__type")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")
        )
        spins_by_type = [
            {
                "type_id": r["case__type_id"],
                "type": r["case__type__type"],
                "name": r["case__type__name"],
                "spins": r["cnt"],
            }
            for r in spins_by_type
        ]

        # ===== 3) Новые пользователи =====
        new_users_count = User.objects.filter(date_joined__gte=dt_from, date_joined__lte=dt_to).count()

        # ===== 4) Новые пользователи от рефералов =====
        # В твоём коде ReferralProfile имеет referred_at — используем его
        new_ref_users_count = ReferralProfile.objects.filter(
            referred_at__gte=dt_from, referred_at__lte=dt_to
        ).count()

        # ===== 5a) Топ пользователей по прокруткам =====
        top_by_spins = (
            spin_q
            .values("user_id", "user__email", "user__username")
            .annotate(spins=Count("id"))
            .order_by("-spins")[:10]
        )
        top_by_spins = [
            {
                "user_id": r["user_id"],
                "email": r["user__email"],
                "username": r["user__username"],
                "spins": r["spins"],
            }
            for r in top_by_spins
        ]

        # ===== 5b) Топ пользователей по прибыли пользователя =====
        # user_profit = sum(prize.amount_usd - case.price_usd)
        user_profit_expr = ExpressionWrapper(F("prize__amount_usd") - F("case__price_usd"),
                                             output_field=DecimalField(max_digits=20, decimal_places=8))
        top_by_user_profit = (
            spin_q
            .values("user_id", "user__email", "user__username")
            .annotate(user_profit=Sum(user_profit_expr))
            .order_by("-user_profit")[:10]
        )
        top_by_user_profit = [
            {
                "user_id": r["user_id"],
                "email": r["user__email"],
                "username": r["user__username"],
                "user_profit_usd": float(r["user_profit"] or 0),
            }
            for r in top_by_user_profit
        ]

        # ===== 6) Всего депозитов/выводов =====
        # Если у статусов есть коды — фильтруем на «завершённые»
        completed_codes = ("done", "approved", "completed", "paid", "success")

        dep_q = Deposit.objects.filter(created_at__gte=dt_from, created_at__lte=dt_to)
        wdr_q = Withdrawal.objects.filter(created_at__gte=dt_from, created_at__lte=dt_to)

        # попробуем отфильтровать завершённые, если есть status__code
        dep_q_completed = dep_q.filter(Q(status__code__in=completed_codes)) if hasattr(Deposit, "status") else dep_q
        wdr_q_completed = wdr_q.filter(Q(status__code__in=completed_codes)) if hasattr(Withdrawal, "status") else wdr_q

        deposits_sum_all = dep_q.aggregate(s=Sum("amount_usd"))["s"] or Decimal("0")
        withdrawals_sum_all = wdr_q.aggregate(s=Sum("amount_usd"))["s"] or Decimal("0")

        deposits_sum_done = dep_q_completed.aggregate(s=Sum("amount_usd"))["s"] or Decimal("0")
        withdrawals_sum_done = wdr_q_completed.aggregate(s=Sum("amount_usd"))["s"] or Decimal("0")

        data = {
            "period": {
                "from": dt_from.isoformat(),
                "to": dt_to.isoformat(),
            },
            "kpis": {
                "profit_usd": float(profit_usd),
                "deposits_sum_usd": float(deposits_sum),
                "wins_usd": float(wins_sum),
                "losses_usd": float(losses_sum),
                "spins_count": int(spins_count),
                "new_users": new_users_count,
                "new_users_from_referrals": new_ref_users_count,
                "deposits": {
                    "sum_all_usd": float(deposits_sum_all),
                    "sum_completed_usd": float(deposits_sum_done),
                },
                "withdrawals": {
                    "sum_all_usd": float(withdrawals_sum_all),
                    "sum_completed_usd": float(withdrawals_sum_done),
                },
            },
            "spins_by_type": spins_by_type,
            "top_users": {
                "by_spins": top_by_spins,
                "by_user_profit": top_by_user_profit,
            },
        }
        return Response(data, status=status.HTTP_200_OK)
