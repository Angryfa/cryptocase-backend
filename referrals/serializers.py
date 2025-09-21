from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ReferralProfile, ReferralBonus

User = get_user_model()

class ReferralInfoSerializer(serializers.Serializer):
    code = serializers.CharField()
    link = serializers.CharField()
    level1_count = serializers.IntegerField()
    level2_count = serializers.IntegerField()
    rewards_l1_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    rewards_l2_total = serializers.DecimalField(max_digits=14, decimal_places=2)

class ReferralBonusSerializer(serializers.ModelSerializer):
    referral_email = serializers.EmailField(source="referral.email", read_only=True)

    class Meta:
        model = ReferralBonus
        fields = ("id", "created_at", "level", "percent", "amount_usd",
                  "deposit_id", "referral_email")
        read_only_fields = fields