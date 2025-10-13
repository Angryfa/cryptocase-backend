# api/views_admin_dashboard.py
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Tuple

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q, Case, When
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from cases.models import Case, CaseType, CasePrize, Spin
from referrals.models import ReferralProfile, ReferralBonus
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
        def get_balance_history(days):
         """
         Возвращает историю общего баланса пользователей.
         Общий баланс = подтвержденные депозиты + реф бонусы - подтвержденные выводы - проигрыши по кейсам на каждую дату.
         """
         history = []
         end_date = timezone.now()
         start_date = end_date - timedelta(days=days-1)
         
         # Статусы завершенных операций
         approved_codes = ("approved", "done", "completed", "paid", "success")
         
         for i in range(days):
            # Конец дня для среза данных
            date_end = timezone.make_aware(
                  datetime.combine(
                     (start_date + timedelta(days=i)).date(),
                     datetime.max.time()
                  )
            )
            
            # Сумма всех одобренных депозитов до этой даты (не от staff/superuser)
            deposits_total = Deposit.objects.filter(
                  status__code__in=approved_codes,
                  processed_at__lte=date_end,
                  user__is_staff=False,
                  user__is_superuser=False
            ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")
            
            # Сумма всех одобренных выводов до этой даты (не от staff/superuser)
            withdrawals_total = Withdrawal.objects.filter(
                  status__code__in=approved_codes,
                  processed_at__lte=date_end,
                  user__is_staff=False,
                  user__is_superuser=False
            ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")

            # Сумма всех реферальных бонусов до этой даты (не от staff/superuser)
            ref_bonuses_total = ReferralBonus.objects.filter(
                created_at__lte=date_end,
                referrer__is_staff=False,
                referrer__is_superuser=False
            ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")
            
            # Сумма всех проигрышей по кейсам до этой даты (не от staff/superuser)
            # Проигрыш = когда prize.amount_usd < case.price_usd, разница идет в минус
            losses_total = Spin.objects.filter(
                created_at__lte=date_end,
                user__is_staff=False,
                user__is_superuser=False
            ).annotate(
                diff=F("case__price_usd") - F("prize__amount_usd")
            ).filter(diff__gt=0).aggregate(total=Sum("diff"))["total"] or Decimal("0")
            
            # Реальный баланс
            real_balance = deposits_total + ref_bonuses_total - withdrawals_total - losses_total
            
            history.append({
                  "date": (start_date + timedelta(days=i)).date().isoformat(),
                  "balance": float(real_balance)
            })
         
         return history
        
        def get_revenue_history(days):
         """
         Возвращает историю дохода платформы.
         Доход = сумма одобренных депозитов - сумма одобренных выводов на каждую дату.
         """
         history = []
         end_date = timezone.now()
         start_date = end_date - timedelta(days=days-1)
         
         approved_codes = ("approved", "done", "completed", "paid", "success")
         
         for i in range(days):
            date_end = timezone.make_aware(
                  datetime.combine(
                     (start_date + timedelta(days=i)).date(),
                     datetime.max.time()
                  )
            )
            
            # Депозиты за этот день
            deposits_day = Deposit.objects.filter(
                  status__code__in=approved_codes,
                  processed_at__lte=date_end,
                  processed_at__gt=date_end - timedelta(days=1),
                  user__is_staff=False,
                  user__is_superuser=False
            ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")
            
            # Выводы за этот день
            withdrawals_day = Withdrawal.objects.filter(
                  status__code__in=approved_codes,
                  processed_at__lte=date_end,
                  processed_at__gt=date_end - timedelta(days=1),
                  user__is_staff=False,
                  user__is_superuser=False
            ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")
            
            # Доход за день
            revenue = deposits_day - withdrawals_day
            
            history.append({
                  "date": (start_date + timedelta(days=i)).date().isoformat(),
                  "revenue": float(revenue)
            })
         
         return history

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
        # ===== Доход по играм =====
        # Case: используем существующие Spin записи
        case_spins = spin_q  # уже отфильтровано по периоду
        case_bets_sum = case_spins.aggregate(
           total=Sum("case__price_usd")
        )["total"] or Decimal("0")

        case_wins_sum = case_spins.aggregate(
           total=Sum("prize__amount_usd")
        )["total"] or Decimal("0")

        case_revenue = case_bets_sum - case_wins_sum
        case_games_count = case_spins.count()

        # Double и Defuse - заглушки (игры пока не реализованы)
        double_revenue = Decimal("0")
        double_bets_sum = Decimal("0")
        double_wins_sum = Decimal("0")
        double_games_count = 0
        
        defuse_revenue = Decimal("0")
        defuse_bets_sum = Decimal("0")
        defuse_wins_sum = Decimal("0")
        defuse_games_count = 0

        game_revenue = {
            "case": {
                "revenue_usd": float(case_revenue),
                "bets_sum": float(case_bets_sum),
                "wins_sum": float(case_wins_sum),
                "games_count": case_games_count,
            },
            "double": {
                "revenue_usd": float(double_revenue),
                "bets_sum": float(double_bets_sum),
                "wins_sum": float(double_wins_sum),
                "games_count": double_games_count,
            },
            "defuse": {
                "revenue_usd": float(defuse_revenue),
                "bets_sum": float(defuse_bets_sum),
                "wins_sum": float(defuse_wins_sum),
                "games_count": defuse_games_count,
            },
        }

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
        # Детали новых пользователей
        new_users_list = User.objects.filter(
            date_joined__gte=dt_from, 
            date_joined__lte=dt_to
         ).select_related('profile', 'referral').values(
            'id', 'username', 'email', 'date_joined',
            'profile__balance_usd', 'profile__deposit_total_usd',
            'referral__referred_by_id'  # если не null, значит реферал
         ).order_by('-date_joined')

        # ===== 4) Новые пользователи от рефералов =====
        # В твоём коде ReferralProfile имеет referred_at — используем его
        new_ref_users_count = ReferralProfile.objects.filter(
            referred_at__gte=dt_from, referred_at__lte=dt_to
        ).count()

        # Общий баланс пользователей (депозиты + реф бонусы - выводы - проигрыши по кейсам)
        approved_codes = ("approved", "done", "completed", "paid", "success")
  
        total_deposits = Deposit.objects.filter(
           status__code__in=approved_codes,
           user__is_staff=False,
           user__is_superuser=False
        ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")
  
        total_withdrawals = Withdrawal.objects.filter(
           status__code__in=approved_codes,
           user__is_staff=False,
           user__is_superuser=False
        ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")

        # Сумма всех реферальных бонусов (не от staff/superuser)
        total_ref_bonuses = ReferralBonus.objects.filter(
            referrer__is_staff=False,
            referrer__is_superuser=False
        ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")
        
        # Сумма всех проигрышей по кейсам (не от staff/superuser)
        # Проигрыш = когда prize.amount_usd < case.price_usd
        total_losses = Spin.objects.filter(
            user__is_staff=False,
            user__is_superuser=False
        ).annotate(
            diff=F("case__price_usd") - F("prize__amount_usd")
        ).filter(diff__gt=0).aggregate(total=Sum("diff"))["total"] or Decimal("0")

        total_users_balance = total_deposits + total_ref_bonuses - total_withdrawals - total_losses
        
        # ===== Реферальные отчисления за последние 24 часа =====
        now = timezone.now()  # используем timezone.now() из django.utils.timezone (уже импортирован на строке 8)
        ref_bonus_24h = ReferralBonus.objects.filter(
            created_at__gte=now - timedelta(hours=24),
            created_at__lte=now
        ).aggregate(total=Sum("amount_usd"))["total"] or Decimal("0")

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
         # что возвращает бэк фронту
        data = {
            "period": {
                "from": dt_from.isoformat(),
                "to": dt_to.isoformat(),
            },
            "new_users_list": list(new_users_list),
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
                "total_users_balance_usd": float(total_users_balance),
                "referral_bonuses_24h_usd": float(ref_bonus_24h),
            },
            "spins_by_type": spins_by_type,
            "top_users": {
                "by_spins": top_by_spins,
                "by_user_profit": top_by_user_profit,
            },
            "balance_history": {
               "7d": get_balance_history(7),
               "30d": get_balance_history(30),
               "365d": get_balance_history(365),
            },
            "revenue_history": {
               "7d": get_revenue_history(7),
               "30d": get_revenue_history(30),
               "365d": get_revenue_history(365),
            },
            "game_revenue": game_revenue,
        }
        return Response(data, status=status.HTTP_200_OK)


class ReferralBonusesListView(APIView):
    """
    Список всех реферальных отчислений с фильтрацией и пагинацией.
    GET /api/admin/referral-bonuses/
    
    Query params:
      - preset: today|yesterday|7d|30d|this_month|prev_month
      - from: ISO8601 datetime
      - to: ISO8601 datetime
      - email: фильтр по email реферера или реферала
      - page: номер страницы (default 1)
      - page_size: размер страницы (default 50)
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Парсим период (используем существующую функцию _parse_period)
        dt_from, dt_to = _parse_period(request)
        
        # Базовый queryset
        qs = ReferralBonus.objects.filter(
            created_at__gte=dt_from,
            created_at__lte=dt_to
        ).select_related(
            'referrer', 'referral', 'deposit', 'deposit__status'
        ).order_by('-created_at')
        
        # Фильтр по email (опционально)
        email = request.query_params.get('email', '').strip()
        if email:
            qs = qs.filter(
                Q(referrer__email__icontains=email) | 
                Q(referral__email__icontains=email)
            )
        
        # Общая сумма за период
        total_sum = qs.aggregate(total=Sum('amount_usd'))['total'] or Decimal('0')
        
        # Пагинация
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = qs.count()
        items = qs[start:end]
        
        # Формируем результат
        data = {
            'period': {
                'from': dt_from.isoformat(),
                'to': dt_to.isoformat(),
            },
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
            },
            'total_sum_usd': float(total_sum),
            'items': [
                {
                    'id': item.id,
                    'created_at': item.created_at.isoformat(),
                    'referrer': {
                        'id': item.referrer.id,
                        'email': item.referrer.email,
                        'username': item.referrer.username,
                    },
                    'referral': {
                        'id': item.referral.id,
                        'email': item.referral.email,
                        'username': item.referral.username,
                    },
                    'deposit': {
                        'id': item.deposit.id,
                        'amount_usd': float(item.deposit.amount_usd),
                        'status': item.deposit.status.name if item.deposit.status else '—',
                    },
                    'level': item.level,
                    'percent': float(item.percent),
                    'amount_usd': float(item.amount_usd),
                }
                for item in items
            ]
        }
        
        return Response(data, status=status.HTTP_200_OK)



class DepositsListView(APIView):
    """
    Эндпоинт для получения списка депозитов с фильтрацией по периодам.
    GET /api/admin/deposits/?preset=7d&page=1&page_size=50
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Парсим период используя существующую функцию
        dt_from, dt_to = _parse_period(request)
        
        # Параметры пагинации
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                page = 1
        except (TypeError, ValueError):
            page = 1
        
        try:
            page_size = int(request.query_params.get("page_size", 50))
            if page_size < 1:
                page_size = 50
            if page_size > 100:
                page_size = 100
        except (TypeError, ValueError):
            page_size = 50
        
        # Фильтруем депозиты по периоду
        # Исключаем депозиты от администраторов
        deposits_qs = Deposit.objects.filter(
            created_at__gte=dt_from,
            created_at__lte=dt_to,
            user__is_staff=False,
            user__is_superuser=False,
        ).select_related("user", "status").order_by("-created_at")
        
        # Общее количество депозитов
        total = deposits_qs.count()
        
        # Пагинация
        start = (page - 1) * page_size
        end = start + page_size
        deposits_page = deposits_qs[start:end]
        
        # Сериализация
        from api.serializers_admin import AdminDepositSerializer
        serializer = AdminDepositSerializer(deposits_page, many=True)
        
        return Response({
            "period": {
                "from": dt_from.isoformat(),
                "to": dt_to.isoformat(),
            },
            "total": total,
            "page": page,
            "page_size": page_size,
            "deposits": serializer.data,
        })

class WithdrawalsListView(APIView):
    """
    Эндпоинт для получения списка выводов с фильтрацией по периодам.
    GET /api/admin/withdrawals/?preset=7d&page=1&page_size=50
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        # Парсим период используя существующую функцию
        dt_from, dt_to = _parse_period(request)
        
        # Параметры пагинации
        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                page = 1
        except (TypeError, ValueError):
            page = 1
        
        try:
            page_size = int(request.query_params.get("page_size", 50))
            if page_size < 1:
                page_size = 50
            if page_size > 100:
                page_size = 100
        except (TypeError, ValueError):
            page_size = 50
        
        # Фильтруем выводы по периоду
        # Исключаем выводы от администраторов
        withdrawals_qs = Withdrawal.objects.filter(
            created_at__gte=dt_from,
            created_at__lte=dt_to,
            user__is_staff=False,
            user__is_superuser=False,
        ).select_related("user", "status").order_by("-created_at")
        
        # Общее количество выводов
        total = withdrawals_qs.count()
        
        # Пагинация
        start = (page - 1) * page_size
        end = start + page_size
        withdrawals_page = withdrawals_qs[start:end]
        
        # Сериализация
        from api.serializers_admin import AdminWithdrawalSerializer
        serializer = AdminWithdrawalSerializer(withdrawals_page, many=True)
        
        return Response({
            "period": {
                "from": dt_from.isoformat(),
                "to": dt_to.isoformat(),
            },
            "total": total,
            "page": page,
            "page_size": page_size,
            "withdrawals": serializer.data,
        })