from rest_framework import serializers
from cases.models import Prize, Case, CasePrize, CaseType
from referrals.models import ReferralLevelConfig
from cashback.models import CashbackSettings
from accounts.models import Deposit, Withdrawal, WithdrawalBlock, DepositBlock, AccountBlock
import json

class AdminCasePrizeInSerializer(serializers.Serializer):
    prize_id = serializers.IntegerField()
    amount_min_usd = serializers.DecimalField(max_digits=14, decimal_places=2)
    amount_max_usd = serializers.DecimalField(max_digits=14, decimal_places=2)
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
            
            prize_id = p.get("prize_id")
            amount_min_usd = p.get("amount_min_usd")
            amount_max_usd = p.get("amount_max_usd")
            weight = p.get("weight", 1)

            if not isinstance(prize_id, int):
                raise serializers.ValidationError(f"prizes[{i}].prize_id обязателен и должен быть числом")
            
            # Проверяем, что приз существует
            try:
                Prize.objects.get(id=prize_id, is_active=True)
            except Prize.DoesNotExist:
                raise serializers.ValidationError(f"prizes[{i}].prize_id: приз с ID {prize_id} не найден или неактивен")
            
            # Валидируем суммы
            try:
                amount_min_usd = float(amount_min_usd)
                amount_max_usd = float(amount_max_usd)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"prizes[{i}].amount_min_usd и amount_max_usd должны быть числами")
            
            if amount_min_usd <= 0 or amount_max_usd <= 0:
                raise serializers.ValidationError(f"prizes[{i}]: суммы должны быть больше 0")
            
            if amount_min_usd > amount_max_usd:
                raise serializers.ValidationError(f"prizes[{i}]: amount_min_usd не может быть больше amount_max_usd")
            
            try:
                weight = int(weight)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"prizes[{i}].weight должно быть целым числом")
            if weight < 1:
                raise serializers.ValidationError(f"prizes[{i}].weight должно быть >= 1")

            cleaned.append({
                "prize_id": prize_id,
                "amount_min_usd": amount_min_usd,
                "amount_max_usd": amount_max_usd,
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
                CasePrize(
                    case=case, 
                    prize_id=p["prize_id"],
                    amount_min_usd=p["amount_min_usd"], 
                    amount_max_usd=p["amount_max_usd"], 
                    weight=p["weight"]
                )
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
                    CasePrize(
                        case=instance, 
                        prize_id=p["prize_id"],
                        amount_min_usd=p["amount_min_usd"], 
                        amount_max_usd=p["amount_max_usd"], 
                        weight=p["weight"]
                    )
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


# Сериализаторы для вложенных данных
class DepositUserSerializer(serializers.Serializer):
    """Информация о пользователе для депозита"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class DepositStatusSerializer(serializers.Serializer):
    """Информация о статусе депозита"""
    code = serializers.CharField()
    name = serializers.CharField()


class AdminDepositSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения депозитов в админке"""
    user = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Deposit
        fields = (
            "id",
            "user",
            "amount_usd",
            "method",
            "details",
            "status",
            "created_at",
            "processed_at",
            "comment",
        )
    
    def get_user(self, obj):
        """Возвращает данные пользователя"""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }
    
    def get_status(self, obj):
        """Возвращает данные статуса"""
        return {
            "code": obj.status.code,
            "name": obj.status.name,
        }

# Сериализаторы для выводов
class WithdrawalUserSerializer(serializers.Serializer):
    """Информация о пользователе для вывода"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class WithdrawalStatusSerializer(serializers.Serializer):
    """Информация о статусе вывода"""
    code = serializers.CharField()
    name = serializers.CharField()


class AdminWithdrawalSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения выводов в админке"""
    user = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Withdrawal
        fields = (
            "id",
            "user",
            "amount_usd",
            "method",
            "details",
            "status",
            "created_at",
            "processed_at",
            "comment",
        )
    
    def get_user(self, obj):
        """Возвращает данные пользователя"""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }
    
    def get_status(self, obj):
        """Возвращает данные статуса"""
        return {
            "code": obj.status.code,
            "name": obj.status.name,
        }


# Сериализаторы для блокировок пользователей
class BaseBlockSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для блокировок"""
    blocked_by = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        """Возвращает данные пользователя"""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }
    
    def get_blocked_by(self, obj):
        """Возвращает данные администратора, который создал блокировку"""
        if obj.blocked_by:
            return {
                "id": obj.blocked_by.id,
                "username": obj.blocked_by.username,
                "email": obj.blocked_by.email,
            }
        return None


class WithdrawalBlockSerializer(BaseBlockSerializer):
    """Сериализатор для блокировок вывода"""
    
    class Meta:
        model = WithdrawalBlock
        fields = (
            "id",
            "user",
            "reason",
            "blocked_by",
            "created_at",
            "is_active",
        )
        read_only_fields = ("id", "created_at", "blocked_by", "user")


class DepositBlockSerializer(BaseBlockSerializer):
    """Сериализатор для блокировок ввода"""
    
    class Meta:
        model = DepositBlock
        fields = (
            "id",
            "user",
            "reason",
            "blocked_by",
            "created_at",
            "is_active",
        )
        read_only_fields = ("id", "created_at", "blocked_by", "user")


class AccountBlockSerializer(BaseBlockSerializer):
    """Сериализатор для блокировок аккаунта"""
    
    class Meta:
        model = AccountBlock
        fields = (
            "id",
            "user",
            "reason",
            "blocked_by",
            "created_at",
            "is_active",
        )
        read_only_fields = ("id", "created_at", "blocked_by", "user")


class WithdrawalBlockCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания блокировок вывода"""
    
    class Meta:
        model = WithdrawalBlock
        fields = ("user", "reason")
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['blocked_by'] = request.user
        
        # Деактивируем предыдущие блокировки вывода для этого пользователя
        WithdrawalBlock.objects.filter(
            user=validated_data['user'],
            is_active=True
        ).update(is_active=False)
        
        return super().create(validated_data)


class DepositBlockCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания блокировок ввода"""
    
    class Meta:
        model = DepositBlock
        fields = ("user", "reason")
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['blocked_by'] = request.user
        
        # Деактивируем предыдущие блокировки ввода для этого пользователя
        DepositBlock.objects.filter(
            user=validated_data['user'],
            is_active=True
        ).update(is_active=False)
        
        return super().create(validated_data)


class AccountBlockCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания блокировок аккаунта"""
    
    class Meta:
        model = AccountBlock
        fields = ("user", "reason")
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['blocked_by'] = request.user
        
        # Деактивируем предыдущие блокировки аккаунта для этого пользователя
        AccountBlock.objects.filter(
            user=validated_data['user'],
            is_active=True
        ).update(is_active=False)
        
        return super().create(validated_data)