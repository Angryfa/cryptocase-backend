from rest_framework import serializers
from cases.models import Case, CasePrize, CaseType
from referrals.models import ReferralLevelConfig
from cashback.models import CashbackSettings


class AdminCasePrizeInSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    amount_usd = serializers.DecimalField(max_digits=14, decimal_places=2)
    weight = serializers.IntegerField(min_value=1, default=1)


class AdminCaseWriteSerializer(serializers.ModelSerializer):
    type_id = serializers.PrimaryKeyRelatedField(source="type", queryset=CaseType.objects.all())
    prizes = AdminCasePrizeInSerializer(many=True, required=False)

    class Meta:
        model = Case
        fields = (
            "id",
            "name",
            "price_usd",
            "is_active",
            "type_id",
            "available_from",
            "available_to",
            "spins_total",
            "spins_used",
            "prizes",
        )
        read_only_fields = ("spins_used",)

    def create(self, validated_data):
        prizes_data = validated_data.pop("prizes", [])
        case = Case.objects.create(**validated_data)
        for p in prizes_data:
            CasePrize.objects.create(case=case, **p)
        return case

    def update(self, instance: Case, validated_data):
        prizes_data = validated_data.pop("prizes", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if prizes_data is not None:
            # Полная замена списка призов для простоты
            instance.prizes.all().delete()
            for p in prizes_data:
                CasePrize.objects.create(case=instance, **p)
        return instance


class AdminCaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = (
            "id",
            "type",
            "name",
            "is_limited",
            "is_timed",
            "sort_order",
            "is_active",
        )


class AdminReferralLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralLevelConfig
        fields = ("id", "level", "percent")


class AdminCashbackSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashbackSettings
        fields = ("id", "enabled", "percent", "period_minutes", "run_minute", "updated_at")


