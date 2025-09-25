from rest_framework import serializers
from cases.models import Case, CasePrize, CaseType
from referrals.models import ReferralLevelConfig
from cashback.models import CashbackSettings
import json

class AdminCasePrizeInSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    amount_usd = serializers.DecimalField(max_digits=14, decimal_places=2)
    weight = serializers.IntegerField(min_value=1, default=1)


class AdminCaseWriteSerializer(serializers.ModelSerializer):
    # тип кейса для записи
    type_id = serializers.PrimaryKeyRelatedField(source="type", queryset=CaseType.objects.all())

    # НОВОЕ: файл-аватар (принимаем через multipart/form-data)
    avatar = serializers.ImageField(required=False, allow_null=True)

    # НОВОЕ: призы (поддержка и обычного списка, и JSON-строки в multipart)
    prizes = AdminCasePrizeInSerializer(many=True, required=False, write_only=True)

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
            "avatar",     # <— добавлено
            "prizes",     # <— write-only вход
        )
        read_only_fields = ("spins_used",)

    def to_internal_value(self, data):
        """
        Делает сериализатор устойчивым к варианту, когда `prizes`
        пришло строкой (JSON) внутри multipart/form-data.
        """
        mutable = data.copy()
        raw = mutable.get("prizes")
        if isinstance(raw, str):
            try:
                mutable["prizes"] = json.loads(raw) if raw.strip() else []
            except json.JSONDecodeError:
                raise serializers.ValidationError({"prizes": "Некорректный JSON"})
        return super().to_internal_value(mutable)

    def create(self, validated_data):
        prizes_data = validated_data.pop("prizes", [])
        case = Case.objects.create(**validated_data)
        if prizes_data:
            CasePrize.objects.bulk_create([
                CasePrize(case=case, **p) for p in prizes_data
            ])
        return case

    def update(self, instance: Case, validated_data):
        prizes_data = validated_data.pop("prizes", None)

        # обновляем поля кейса, включая avatar (если пришёл)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        # политика упрощённая: полная замена призов при передаче prizes
        if prizes_data is not None:
            instance.prizes.all().delete()
            if prizes_data:
                CasePrize.objects.bulk_create([
                    CasePrize(case=instance, **p) for p in prizes_data
                ])
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


