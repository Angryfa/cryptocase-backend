from rest_framework import serializers
from cases.models import Prize, Case, CasePrize, CaseType, Spin
from referrals.models import ReferralLevelConfig
from cashback.models import CashbackSettings
from accounts.models import Deposit, Withdrawal, WithdrawalBlock, DepositBlock, AccountBlock
from promocodes.models import Promocode, PromocodeActivation
import json
from django.db import transaction
from decimal import Decimal, InvalidOperation

class AdminCasePrizeInSerializer(serializers.Serializer):
    prize_id = serializers.IntegerField()
    amount_min_usd = serializers.DecimalField(max_digits=14, decimal_places=2)
    amount_max_usd = serializers.DecimalField(max_digits=14, decimal_places=2)
    weight = serializers.IntegerField(min_value=1, default=1)


class AdminCaseWriteSerializer(serializers.ModelSerializer):
    type_id = serializers.PrimaryKeyRelatedField(source="type", queryset=CaseType.objects.all())
    avatar = serializers.ImageField(required=False, allow_null=True)
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
            "avatar",
            "prizes",
        )
        read_only_fields = ("spins_used",)

    # ---- Валидация входных призов: поддержка 2 форматов ----
    def validate_prizes(self, value):
        if value in (None, ""):
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("prizes должен быть массивом объектов")

        cleaned = []
        for i, p in enumerate(value):
            if not isinstance(p, dict):
                raise serializers.ValidationError(f"prizes[{i}] должен быть объектом")

            pid = p.get("id", None)              # id записи CasePrize (для UPSERT)
            weight = p.get("weight", 1)

            # Канонический формат: prize_id + min/max
            if "prize_id" in p or "amount_min_usd" in p or "amount_max_usd" in p:
                prize_id = p.get("prize_id")
                amt_min = p.get("amount_min_usd")
                amt_max = p.get("amount_max_usd")

                if not isinstance(prize_id, int):
                    raise serializers.ValidationError(f"prizes[{i}].prize_id обязателен и должен быть числом")

                try:
                    Prize.objects.get(id=prize_id, is_active=True)
                except Prize.DoesNotExist:
                    raise serializers.ValidationError(f"prizes[{i}].prize_id: приз {prize_id} не найден или неактивен")

                try:
                    amt_min = Decimal(str(amt_min))
                    amt_max = Decimal(str(amt_max))
                except (InvalidOperation, TypeError, ValueError):
                    raise serializers.ValidationError(f"prizes[{i}].amount_min_usd и amount_max_usd должны быть числами")

                if amt_min <= 0 or amt_max <= 0:
                    raise serializers.ValidationError(f"prizes[{i}]: суммы должны быть > 0")
                if amt_min > amt_max:
                    raise serializers.ValidationError(f"prizes[{i}]: amount_min_usd не может быть больше amount_max_usd")

                try:
                    weight = int(weight)
                except (TypeError, ValueError):
                    raise serializers.ValidationError(f"prizes[{i}].weight должно быть целым числом")
                if weight < 1:
                    raise serializers.ValidationError(f"prizes[{i}].weight должно быть >= 1")

                item = {
                    "schema": "fk",
                    "prize_id": prize_id,
                    "amount_min_usd": amt_min,
                    "amount_max_usd": amt_max,
                    "weight": weight,
                }

            # Устаревший формат: title + amount_usd
            elif "title" in p or "amount_usd" in p:
                title = p.get("title")
                amount_usd = p.get("amount_usd")

                if not isinstance(title, str) or not title.strip():
                    raise serializers.ValidationError(f"prizes[{i}].title обязателен")

                try:
                    amount_usd = Decimal(str(amount_usd))
                except (InvalidOperation, TypeError, ValueError):
                    raise serializers.ValidationError(f"prizes[{i}].amount_usd должно быть числом")

                if amount_usd <= 0:
                    raise serializers.ValidationError(f"prizes[{i}].amount_usd должно быть > 0")

                try:
                    weight = int(weight)
                except (TypeError, ValueError):
                    raise serializers.ValidationError(f"prizes[{i}].weight должно быть целым числом")
                if weight < 1:
                    raise serializers.ValidationError(f"prizes[{i}].weight должно быть >= 1")

                # Сохраняем в устаревшие поля, диапазон ставим min=max=amount_usd
                item = {
                    "schema": "legacy",
                    "title": title.strip(),
                    "amount_usd": amount_usd,
                    "amount_min_usd": amount_usd,
                    "amount_max_usd": amount_usd,
                    "weight": weight,
                    "prize_id": None,  # явное отсутствие FK
                }

            else:
                raise serializers.ValidationError(
                    f"prizes[{i}]: ожидаются поля либо (prize_id, amount_min_usd, amount_max_usd[, weight]), "
                    f"либо (title, amount_usd[, weight])"
                )

            if pid not in (None, "", 0):
                try:
                    item["id"] = int(pid)
                except (TypeError, ValueError):
                    raise serializers.ValidationError(f"prizes[{i}].id должен быть целым")

            cleaned.append(item)

        return cleaned

    def _create_case_prizes(self, case, prizes_data):
        """Вставка призов при create."""
        to_create = []
        for p in prizes_data:
            if p["schema"] == "fk":
                to_create.append(CasePrize(
                    case=case,
                    prize_id=p["prize_id"],
                    amount_min_usd=p["amount_min_usd"],
                    amount_max_usd=p["amount_max_usd"],
                    weight=p["weight"],
                    # чистим устаревшие поля
                    title=None,
                    amount_usd=None,
                ))
            else:  # legacy
                to_create.append(CasePrize(
                    case=case,
                    prize=None,
                    title=p["title"],
                    amount_usd=p["amount_usd"],
                    amount_min_usd=p["amount_min_usd"],
                    amount_max_usd=p["amount_max_usd"],
                    weight=p["weight"],
                ))
        if to_create:
            CasePrize.objects.bulk_create(to_create)

    def _upsert_case_prizes(self, case, prizes_data):
        """
        UPSERT по id: обновить существующие, создать новые; удалить отсутствующие,
        если по ним нет Spin (учитываем и case_prize, и старую ссылку prize).
        """
        existing = {cp.id: cp for cp in case.prizes.all()}
        seen_ids = set()

        # 1) обновления/создания
        for item in prizes_data or []:
            rec_id = item.get("id")

            if rec_id and rec_id in existing:
                cp = existing[rec_id]
                if item["schema"] == "fk":
                    cp.prize_id = item["prize_id"]
                    cp.title = None
                    cp.amount_usd = None
                    cp.amount_min_usd = item["amount_min_usd"]
                    cp.amount_max_usd = item["amount_max_usd"]
                    cp.weight = item["weight"]
                else:
                    cp.prize = None
                    cp.title = item["title"]
                    cp.amount_usd = item["amount_usd"]
                    cp.amount_min_usd = item["amount_min_usd"]
                    cp.amount_max_usd = item["amount_max_usd"]
                    cp.weight = item["weight"]
                cp.save()
                seen_ids.add(rec_id)
            else:
                if item["schema"] == "fk":
                    obj = CasePrize.objects.create(
                        case=case,
                        prize_id=item["prize_id"],
                        amount_min_usd=item["amount_min_usd"],
                        amount_max_usd=item["amount_max_usd"],
                        weight=item["weight"],
                        title=None,
                        amount_usd=None,
                    )
                else:
                    obj = CasePrize.objects.create(
                        case=case,
                        prize=None,
                        title=item["title"],
                        amount_usd=item["amount_usd"],
                        amount_min_usd=item["amount_min_usd"],
                        amount_max_usd=item["amount_max_usd"],
                        weight=item["weight"],
                    )
                seen_ids.add(obj.id)

        # 2) удаления безопасные
        to_delete = [cp for cid, cp in existing.items() if cid not in seen_ids]
        if to_delete:
            deletable, blocked = [], []
            for cp in to_delete:
                has_spins = Spin.objects.filter(
                    models.Q(case_prize=cp) | models.Q(prize=cp)
                ).exists()
                if has_spins:
                    blocked.append(cp.id)
                else:
                    deletable.append(cp.id)

            if deletable:
                CasePrize.objects.filter(id__in=deletable).delete()

            if blocked:
                raise serializers.ValidationError({
                    "prizes": (
                        "Нельзя удалить некоторые призы, т.к. на них существуют крутки (Spin). "
                        "Оставьте их в списке. Заблокированные ID: %(ids)s"
                    ) % {"ids": blocked}
                })

    def create(self, validated_data):
        avatar = validated_data.pop("avatar", None)
        prizes_data = validated_data.pop("prizes", [])

        case = Case.objects.create(**validated_data)
        if avatar is not None:
            case.avatar = avatar
            case.save(update_fields=["avatar"])

        if prizes_data:
            self._create_case_prizes(case, prizes_data)

        return case

    @transaction.atomic
    def update(self, instance: Case, validated_data):
        avatar = validated_data.pop("avatar", None)
        prizes_present = "prizes" in validated_data
        prizes_data = validated_data.pop("prizes", None)

        # обновляем поля кейса
        for field, value in validated_data.items():
            setattr(instance, field, value)

        if avatar is not None:
            instance.avatar = avatar

        instance.save()

        if not prizes_present:
            return instance

        # UPSERT состава призов
        self._upsert_case_prizes(instance, prizes_data or [])
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


# =====================
# Промокоды — админка
# =====================

class AdminPromocodeSerializer(serializers.ModelSerializer):
    remaining_activations = serializers.IntegerField(read_only=True)

    class Meta:
        model = Promocode
        fields = (
            "id",
            "code",
            "promo_type",
            "amount_usd",
            "max_activations",
            "is_active",
            "starts_at",
            "ends_at",
            "remaining_activations",
            "created_at",
            "updated_at",
        )


class AdminPromocodeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = (
            "code",
            "promo_type",
            "amount_usd",
            "max_activations",
            "is_active",
            "starts_at",
            "ends_at",
        )

    def validate_amount_usd(self, value):
        if value is None:
            return value
        if value < 0:
            raise serializers.ValidationError("Номинал не может быть отрицательным")
        return value

    def validate_max_activations(self, value):
        if value is None:
            return value
        if value < 0:
            raise serializers.ValidationError("Количество активаций не может быть отрицательным")
        return value


class AdminPromocodeActivationSerializer(serializers.ModelSerializer):
    promocode = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = PromocodeActivation
        fields = (
            "id",
            "promocode",
            "user",
            "amount_usd",
            "created_at",
        )

    def get_promocode(self, obj):
        p = obj.promocode
        return {"id": p.id, "code": p.code}

    def get_user(self, obj):
        u = obj.user
        return {"id": u.id, "email": getattr(u, "email", ""), "username": getattr(u, "username", "")}        


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