from rest_framework import serializers
from decimal import Decimal
from .models import Prize, CaseType, Case, CasePrize, Spin, BonusSpin

class PrizeSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Prize
        fields = ("id", "name", "image", "image_url", "is_active", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ("id", "type", "name", "is_limited", "is_timed")

class CasePrizeSerializer(serializers.ModelSerializer):
    prize = PrizeSerializer(read_only=True)
    prize_id = serializers.PrimaryKeyRelatedField(
        source="prize", queryset=Prize.objects.all(), write_only=True, required=False
    )
    
    # Для обратной совместимости
    title = serializers.SerializerMethodField()
    amount_usd = serializers.SerializerMethodField()
    
    class Meta:
        model = CasePrize
        fields = (
            "id", "prize", "prize_id", 
            "amount_min_usd", "amount_max_usd", "weight",
            "title", "amount_usd"  # Для обратной совместимости
        )
    
    def get_title(self, obj):
        return obj.prize.name if obj.prize else obj.title
    
    def get_amount_usd(self, obj):
        return obj.amount_min_usd if obj.amount_min_usd else obj.amount_usd

class CaseSerializer(serializers.ModelSerializer):
    type = CaseTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        source="type", queryset=CaseType.objects.all(), write_only=True, required=False
    )

    # НОВОЕ: аватар (загрузка файла) и его URL (для чтения)
    avatar = serializers.ImageField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

    spins_remaining = serializers.IntegerField(read_only=True)
    is_available_now = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = (
            "id", "name", "price_usd", "is_active",
            "type", "type_id",
            "available_from", "available_to",
            "spins_total", "spins_used", "spins_remaining",
            "is_available_now",
            "avatar",        # <- принимает файл при POST/PUT/PATCH (multipart/form-data)
            "avatar_url",    # <- отдаёт абсолютный URL
        )

    def get_is_available_now(self, obj):
        return obj.is_available_now()

    def get_avatar_url(self, obj):
        if not getattr(obj, "avatar", None):
            return None
        try:
            url = obj.avatar.url
        except ValueError:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

class CaseDetailSerializer(CaseSerializer):
    prizes = CasePrizeSerializer(many=True, read_only=True)
    class Meta(CaseSerializer.Meta):
        fields = CaseSerializer.Meta.fields + (
            "prizes",
            # Бонусная система:
            "bonus_chance",
            "bonus_type_chance_multiplier",
            "bonus_multipliers",
            "max_bonus_opens",
        )

class SpinSerializer(serializers.ModelSerializer):
    case_prize = CasePrizeSerializer(read_only=True)
    prize = serializers.SerializerMethodField(read_only=True)  # Для обратной совместимости
    prize_title = serializers.SerializerMethodField(read_only=True)
    amount_usd = serializers.SerializerMethodField(read_only=True)  # Для обратной совместимости

    case_name = serializers.CharField(source="case.name", read_only=True)
    case_id = serializers.IntegerField(source="case.id", read_only=True)

    # Бонусная система
    bonus_type_display = serializers.SerializerMethodField(read_only=True)
    bonus_description = serializers.SerializerMethodField(read_only=True)
    bonus_spins_list = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Spin
        fields = (
            "id", "created_at",
            "case", "case_id", "case_name", 
            "case_prize", "prize", "prize_title", "amount_usd", "actual_amount_usd",
            # Бонусная система:
            "has_bonus",
            "bonus_type",
            "bonus_type_display",
            "bonus_multiplier",
            "base_amount_usd",
            "bonus_spins",  # Старое JSON поле для обратной совместимости
            "bonus_spins_list",  # Новое поле из связанных BonusSpin записей
            "bonus_description",
            # Provably Fair:
            "server_seed_hash",
            "server_seed",        # если не хочешь светить сразу — просто убери эту строку
            "client_seed",
            "nonce",
            "roll_digest",
            "rng_value",
            "weights_snapshot",
        )
        read_only_fields = fields
    
    def get_bonus_type_display(self, obj):
        """Отображаемое название типа бонуса"""
        if obj.has_bonus and obj.bonus_type:
            return dict(Spin.BONUS_TYPE_CHOICES).get(obj.bonus_type, obj.bonus_type)
        return None
    
    def get_bonus_spins_list(self, obj):
        """Получает список дополнительных открытий из связанных BonusSpin записей"""
        try:
            # Пытаемся получить связанные BonusSpin записи
            bonus_spins = obj.bonus_spin_records.all() if hasattr(obj, 'bonus_spin_records') else []
            return [
                {
                    "bonus_spin_id": bs.id,
                    "spin_id": bs.id,  # Для обратной совместимости
                    "amount": str(bs.actual_amount_usd),
                    "bonus_type": None,
                    "is_extra_open": True,
                    "nonce": bs.nonce,
                }
                for bs in bonus_spins
            ]
        except Exception:
            # Если связанные записи недоступны, возвращаем старое JSON поле
            return obj.bonus_spins if isinstance(obj.bonus_spins, list) else []
    
    def get_bonus_description(self, obj):
        """Описание бонуса для отображения"""
        if not obj.has_bonus:
            return None
        
        if obj.bonus_type == "multiplier" and obj.bonus_multiplier:
            return f"x{obj.bonus_multiplier}"
        elif obj.bonus_type == "extra_open":
            # Используем bonus_spins_list если доступен, иначе старое поле
            bonus_spins_data = self.get_bonus_spins_list(obj) or (obj.bonus_spins if isinstance(obj.bonus_spins, list) else [])
            if bonus_spins_data:
                total_bonus = sum(Decimal(str(spin.get("amount", 0))) for spin in bonus_spins_data)
                return f"Доп. открытие (+${total_bonus:.2f})"
        return None
    
    def get_prize(self, obj):
        """Для обратной совместимости"""
        if obj.case_prize:
            return CasePrizeSerializer(obj.case_prize, context=self.context).data
        elif obj.prize:
            return CasePrizeSerializer(obj.prize, context=self.context).data
        return None
    
    def get_prize_title(self, obj):
        """Для обратной совместимости"""
        if obj.case_prize:
            if obj.case_prize.prize:
                return obj.case_prize.prize.name
            elif obj.case_prize.title:
                return obj.case_prize.title
        elif obj.prize:
            return obj.prize.prize_name
        return "Неизвестный приз"
    
    def get_amount_usd(self, obj):
        """Для обратной совместимости"""
        if obj.actual_amount_usd:
            return obj.actual_amount_usd
        elif obj.prize and obj.prize.amount_usd:
            return obj.prize.amount_usd
        return None


class BonusSpinSerializer(serializers.ModelSerializer):
    """Сериализатор для дополнительных открытий"""
    case_name = serializers.CharField(source="case.name", read_only=True)
    case_id = serializers.IntegerField(source="case.id", read_only=True)
    parent_spin_id = serializers.IntegerField(source="parent_spin.id", read_only=True)
    prize_title = serializers.SerializerMethodField(read_only=True)
    amount_usd = serializers.DecimalField(source="actual_amount_usd", max_digits=14, decimal_places=2, read_only=True)
    
    class Meta:
        model = BonusSpin
        fields = (
            "id",
            "parent_spin_id",
            "case_id",
            "case_name",
            "case_prize",
            "prize_title",
            "amount_usd",
            "actual_amount_usd",
            "created_at",
            # Provably Fair:
            "server_seed_hash",
            "server_seed",
            "client_seed",
            "nonce",
            "roll_digest",
            "rng_value",
            "weights_snapshot",
        )
        read_only_fields = fields
    
    def get_prize_title(self, obj):
        """Для обратной совместимости"""
        if obj.case_prize:
            if obj.case_prize.prize:
                return obj.case_prize.prize.name
            elif obj.case_prize.title:
                return obj.case_prize.title
        return "Неизвестный приз"


class SpinListSerializer(serializers.ModelSerializer):
    case_id   = serializers.IntegerField(source="case.id", read_only=True)
    case_name = serializers.CharField(source="case.name", read_only=True)
    prize_title = serializers.SerializerMethodField(read_only=True)
    amount_usd  = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Spin
        fields = ("id", "created_at", "case_id", "case_name", "prize_title", "amount_usd")
        read_only_fields = fields
    
    def get_prize_title(self, obj):
        """Для обратной совместимости"""
        if obj.case_prize:
            if obj.case_prize.prize:
                return obj.case_prize.prize.name
            elif obj.case_prize.title:
                return obj.case_prize.title
        elif obj.prize:
            return obj.prize.prize_name
        return "Неизвестный приз"
    
    def get_amount_usd(self, obj):
        """Для обратной совместимости"""
        if obj.actual_amount_usd:
            return obj.actual_amount_usd
        elif obj.prize and obj.prize.amount_usd:
            return obj.prize.amount_usd
        return None