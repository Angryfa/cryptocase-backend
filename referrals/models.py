from django.conf import settings
from django.db import models
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
