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
    prizes = serializers.JSONField(required=False, write_only=True)

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
    
    def validate_prizes(self, value):
        """
        Приходит либо уже распарсенный список, либо строка — JSONField сам распарсит.
        Здесь аккуратно валидируем структуру без deepcopy файлов.
        """
        if value in (None, ""):
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("prizes должен быть массивом объектов")

        cleaned = []
        for i, p in enumerate(value):
            if not isinstance(p, dict):
                raise serializers.ValidationError(f"prizes[{i}] должен быть объектом")
            title = p.get("title")
            amount_usd = p.get("amount_usd")
            weight = p.get("weight", 1)

            if not isinstance(title, str) or not title.strip():
                raise serializers.ValidationError(f"prizes[{i}].title обязателен")
            # допускаем число или строку с числом
            try:
                amount_usd = float(amount_usd)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"prizes[{i}].amount_usd должно быть числом")
            try:
                weight = int(weight)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"prizes[{i}].weight должно быть целым")
            if weight < 1:
                raise serializers.ValidationError(f"prizes[{i}].weight >= 1")

            cleaned.append({
                "title": title.strip(),
                "amount_usd": amount_usd,
                "weight": weight,
            })
        return cleaned
    

    def create(self, validated_data):
        # РАНО вырезаем файл (до любых манипуляций с прочими данными)
        avatar = validated_data.pop("avatar", None)
        prizes_data = validated_data.pop("prizes", [])
        case = Case.objects.create(**validated_data)
        if avatar is not None:
            case.avatar = avatar
            case.save(update_fields=["avatar"])
        if prizes_data:
            CasePrize.objects.bulk_create([
                CasePrize(case=case, title=p["title"], amount_usd=p["amount_usd"], weight=p["weight"])
                for p in prizes_data
            ])
        return case

    def update(self, instance: Case, validated_data):
        # РАНО вырезаем файл
        avatar = validated_data.pop("avatar", None)
        prizes_data = validated_data.pop("prizes", None)

        # обновляем поля кейса, включая avatar (если пришёл)
        for field, value in validated_data.items():
            setattr(instance, field, value)
         # Обновляем аватар (если прислали ключ avatar — даже если он None, можно трактовать как “очистить”)
        if avatar is not None:
            instance.avatar = avatar

        instance.save()

        # политика упрощённая: полная замена призов при передаче prizes
        if prizes_data is not None:
            instance.prizes.all().delete()
            if prizes_data:
                CasePrize.objects.bulk_create([
                    CasePrize(case=instance, title=p["title"], amount_usd=p["amount_usd"], weight=p["weight"])
                    for p in prizes_data
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


