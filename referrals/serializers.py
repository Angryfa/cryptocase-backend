from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ReferralProfile, ReferralReward

User = get_user_model()

class ReferralInfoSerializer(serializers.Serializer):
    code = serializers.CharField()
    link = serializers.CharField()
    level1_count = serializers.IntegerField()
    level2_count = serializers.IntegerField()
    rewards_l1_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    rewards_l2_total = serializers.DecimalField(max_digits=14, decimal_places=2)
