from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ReferralProfile, gen_code

User = get_user_model()

@receiver(post_save, sender=User)
def create_referral_profile(sender, instance, created, **kwargs):
    if not created:
        return
    code = gen_code()
    while ReferralProfile.objects.filter(code=code).exists():
        code = gen_code()
    ReferralProfile.objects.create(user=instance, code=code)
