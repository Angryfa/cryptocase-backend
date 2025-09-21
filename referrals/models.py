from django.conf import settings
from django.db import models
from decimal import Decimal
import secrets

User = settings.AUTH_USER_MODEL

def gen_code(length=8):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # без O/0/I/1
    return "".join(secrets.choice(alphabet) for _ in range(length))

class ReferralProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referral")
    code = models.CharField(max_length=16, unique=True, db_index=True)
    referred_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals_l1"
    )
    referred_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ReferralProfile<{self.user}>"


class ReferralLevelConfig(models.Model):
    """Настройки процентов по уровням рефералок.

    Примеры записей:
      level=1, percent=10.00
      level=2, percent=5.00
    """
    level = models.PositiveIntegerField(unique=True, db_index=True)
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "Процент рефералов (уровень)"
        verbose_name_plural = "Проценты рефералов (уровни)"
        ordering = ("level",)

    def __str__(self):
        return f"L{self.level}: {self.percent}%"

class ReferralBonus(models.Model):
    """История начислений рефереру за депозиты его рефералов."""
    class Level(models.IntegerChoices):
        L1 = 1, "Уровень 1"
        L2 = 2, "Уровень 2"

    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referral_bonuses")
    referral = models.ForeignKey(User, on_delete=models.CASCADE, related_name="made_referral_deposits")
    deposit  = models.ForeignKey("accounts.Deposit", on_delete=models.PROTECT, related_name="referral_bonuses")

    level      = models.PositiveSmallIntegerField(choices=Level.choices)          # 1 или 2
    percent    = models.DecimalField(max_digits=5, decimal_places=2)              # сколько %, например 10.00
    amount_usd = models.DecimalField(max_digits=14, decimal_places=2)             # начисленная сумма в USD

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Реферальный бонус"
        verbose_name_plural = "Реферальные бонусы"
        unique_together = (("deposit", "level"),)  # защита от повторного начисления
        indexes = [
            models.Index(fields=["referrer"]),
            models.Index(fields=["deposit"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ("-created_at",)

    def __str__(self):
        return f"Bonus L{self.level} {self.amount_usd} → {self.referrer}"