from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone

from cashback.models import CashbackSettings, CashbackAccrual
from accounts.models import Deposit, DepositStatus, Withdrawal, WithdrawalStatus

User = get_user_model()

class Command(BaseCommand):
    help = "Рассчитать кэшбэк как снимок на конкретный момент времени (без зачисления на баланс)."

    def add_arguments(self, parser):
        # момент расчёта (ISO). Если не задан, берём 'сейчас', выровненный по run_minute.
        parser.add_argument("--at", type=str, default=None,
                            help="Момент расчёта (ISO), напр. '2025-09-05T10:00:00Z'. По умолчанию — текущее время, выровненное по run_minute.")
        parser.add_argument("--percent", type=str, default=None,
                            help="Переопределить процент на один запуск, напр. '10.0'")
        parser.add_argument("--dry-run", action="store_true",
                            help="Не писать в БД, только вывести план.")
        # опционально: перезаписывать запись, если запуск повторился в ту же минуту
        parser.add_argument("--upsert", action="store_true",
                            help="Если запись на этот момент уже есть — обновить сумму вместо пропуска.")

    def _align_to_run_minute(self, now, run_minute):
        """Выровнять время к минуте run_minute текущего часа, не уводя в будущее."""
        aligned = now.replace(minute=run_minute, second=0, microsecond=0)
        # если выравнивание оказалось в будущем — берём прошлый час
        if aligned > now:
            aligned = aligned - timezone.timedelta(hours=1)
        return aligned

    def handle(self, *args, **opts):
        settings = CashbackSettings.objects.first()
        if not settings or not settings.enabled:
            self.stdout.write(self.style.WARNING("Cashback disabled or not configured."))
            return

        percent = Decimal(opts["percent"]) if opts["percent"] else settings.percent
        run_minute = int(settings.run_minute or 0)

        # МОМЕНТ РАСЧЁТА (as-of)
        if opts["at"]:
            try:
                asof = timezone.datetime.fromisoformat(opts["at"].replace("Z","+00:00"))
                if timezone.is_naive(asof):
                    asof = timezone.make_aware(asof, timezone.get_current_timezone())
            except Exception:
                return self.stdout.write(self.style.ERROR("Bad --at format, use ISO 8601"))
        else:
            asof = self._align_to_run_minute(timezone.now(), run_minute)

        dep_ok = DepositStatus.objects.filter(code="approved").first()
        wdr_ok = WithdrawalStatus.objects.filter(code="approved").first()
        if not dep_ok or not wdr_ok:
            return self.stdout.write(self.style.ERROR("Need DepositStatus/WithdrawalStatus(code='approved')"))

        users = User.objects.all()
        created, updated, skipped = 0, 0, 0

        for u in users:
            # Кумулятивные суммы на момент asof
            dep_sum = (
                Deposit.objects
                .filter(user=u, status=dep_ok, processed_at__lte=asof)
                .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00")
            )
            wdr_sum = (
                Withdrawal.objects
                .filter(user=u, status=wdr_ok, processed_at__lte=asof)
                .aggregate(s=Sum("amount_usd"))["s"] or Decimal("0.00")
            )
            base_net = dep_sum - wdr_sum
            if base_net <= 0:
                skipped += 1
                continue

            amount = (base_net * percent / Decimal("100")).quantize(Decimal("0.01"))

            # Используем slot_started_at как «момент расчёта», чтобы не городить миграции
            # unique_together = (user, slot_started_at) уже предотвращает дубли
            existing = CashbackAccrual.objects.filter(user=u, slot_started_at=asof).first()