from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32, blank=True)

    # 💰 финансы
    balance_usd        = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    deposit_total_usd  = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    won_total_usd      = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    lost_total_usd     = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"
