from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import os, base64

def _gen_client_seed():
    return base64.b16encode(os.urandom(16)).decode().lower()  # 32 hex

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32, blank=True)

    # 💰 финансы
    balance_usd        = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    deposit_total_usd  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    won_total_usd      = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    lost_total_usd     = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    # NEW: Provably Fair
    client_seed = models.CharField(max_length=64, default=_gen_client_seed, db_index=True,null=True, blank=True)
    pf_nonce = models.PositiveIntegerField(default=0, help_text="Счётчик прокруток для текущего client_seed")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"
    def next_nonce(self):
        # вызывать внутри select_for_update()
        self.pf_nonce = (self.pf_nonce or 0) + 1
        self.save(update_fields=["pf_nonce", "updated_at"])
        return self.pf_nonce

class WithdrawalStatus(models.Model):
    """Справочник статусов заявок на вывод."""
    code = models.CharField(max_length=32, unique=True)  # 'pending' | 'approved' | 'rejected' | 'cancelled'
    name = models.CharField(max_length=64)               # Человекочитаемое имя

    class Meta:
        verbose_name = "Статус вывода"
        verbose_name_plural = "Статусы вывода"
        ordering = ("code",)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdrawals")
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2)
    method = models.CharField(max_length=50, blank=True)     # USDT-TRC20 / Bank и т.п.
    details = models.CharField(max_length=255, blank=True)   # адрес/реквизиты

    # ⬇️ FK вместо CharField
    status = models.ForeignKey(WithdrawalStatus, on_delete=models.PROTECT, related_name="withdrawals")

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at", "id")

    def __str__(self):
        return f"Withdrawal<{self.id}> {self.user} ${self.amount_usd} [{self.status}]"
    
class DepositStatus(models.Model):
    code = models.CharField(max_length=32, unique=True)  # 'pending' | 'approved' | 'rejected' | 'cancelled'
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "Статус депозита"
        verbose_name_plural = "Статусы депозитов"
        ordering = ("code",)

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deposits")
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2)
    method = models.CharField(max_length=50, blank=True)    # например: USDT-TRC20 / Bank
    details = models.CharField(max_length=255, blank=True)  # адрес/реквизиты/комментарий
    status = models.ForeignKey(DepositStatus, on_delete=models.PROTECT, related_name="deposits")

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)  # причина отклонения и т.д.

    class Meta:
        ordering = ("-created_at", "id")

    def __str__(self):
        return f"Deposit<{self.id}> {self.user} ${self.amount_usd} [{self.status}]"