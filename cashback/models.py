from decimal import Decimal, ROUND_DOWN
from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class CashbackSettings(models.Model):
    """
    Единые настройки:
    - percent: процент кэшбэка (например, 10.00 означает 10%)
    - period_minutes: период расчёта в минутах (по умолчанию 60 = каждый час)
    - run_minute: минута часа, когда выполнять (0..59) — для красоты слота
    - enabled: флаг включения
    """
    enabled = models.BooleanField(default=True)
    percent = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("10.00"))
    period_minutes = models.PositiveIntegerField(default=60)
    run_minute = models.PositiveSmallIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки кэшбэка"
        verbose_name_plural = "Настройки кэшбэка"

    def str(self):
        return f"CashbackSettings(enabled={self.enabled}, {self.percent}% / {self.period_minutes}m)"


class CashbackAccrual(models.Model):
    """
    Факт рассчитанного кэшбэка (пока без зачисления на баланс).
    - user: кому рассчитали
    - amount_usd: сумма кэшбэка
    - base_deposits_usd / base_withdrawals_usd / base_net_usd: база расчёта на момент вычисления
    - percent_used: какой процент применили
    - slot_started_at: начало временного слота (например, час, к которому относится расчёт)
    - computed_at: когда посчитали
    - status: calculated|credited|cancelled (на будущее)
    """
    STATUS_CALCULATED = "calculated"
    STATUS_CREDITED   = "credited"
    STATUS_CANCELLED  = "cancelled"
    STATUS_CHOICES = [
        (STATUS_CALCULATED, "Рассчитан"),
        (STATUS_CREDITED,   "Зачислен"),
        (STATUS_CANCELLED,  "Отменён"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cashback_accruals")
    amount_usd = models.DecimalField(max_digits=16, decimal_places=2)

    base_deposits_usd = models.DecimalField(max_digits=16, decimal_places=2)
    base_withdrawals_usd = models.DecimalField(max_digits=16, decimal_places=2)
    base_net_usd = models.DecimalField(max_digits=16, decimal_places=2)

    percent_used = models.DecimalField(max_digits=6, decimal_places=2)

    slot_started_at = models.DateTimeField(db_index=True)
    computed_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_CALCULATED, db_index=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Начисление кэшбэка"
        verbose_name_plural = "Начисления кэшбэка"
        ordering = ("-computed_at", "id")
        unique_together = (("user", "slot_started_at"),)  # один расчет на пользователя в слоте

    def str(self):
        return f"CashbackAccrual<{self.id}> {self.user} ${self.amount_usd} @ {self.slot_started_at}"

    @staticmethod
    def quant2(v: Decimal) -> Decimal:
        return (v or Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_DOWN)