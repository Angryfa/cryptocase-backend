from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers
from .models import Profile, Deposit

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser", "date_joined")

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    # финансовые поля выдаём read-only (чтобы нельзя было PATCH-ем подкрутить баланс)
    class Meta:
        model = Profile
        fields = ("phone", "balance_usd", "deposit_total_usd", "won_total_usd", "lost_total_usd")
        read_only_fields = ("balance_usd", "deposit_total_usd", "won_total_usd", "lost_total_usd")

class UserWithProfileSerializer(UserPublicSerializer):
    profile = ProfileSerializer(read_only=True)
    approved_deposits_total = serializers.SerializerMethodField()
    approved_withdrawals_total = serializers.SerializerMethodField()

    class Meta(UserPublicSerializer.Meta):
        fields = UserPublicSerializer.Meta.fields + ("profile", "approved_deposits_total", "approved_withdrawals_total")
    
    def get_approved_deposits_total(self, obj):
        from .models import Deposit, DepositStatus
        approved_status = DepositStatus.objects.filter(code="approved").first()
        if approved_status:
            total = Deposit.objects.filter(user=obj, status=approved_status).aggregate(
                total=models.Sum('amount_usd')
            )['total']
            return float(total or 0)
        return 0.0
    
    def get_approved_withdrawals_total(self, obj):
        from .models import Withdrawal, WithdrawalStatus
        approved_status = WithdrawalStatus.objects.filter(code="approved").first()
        if approved_status:
            total = Withdrawal.objects.filter(user=obj, status=approved_status).aggregate(
                total=models.Sum('amount_usd')
            )['total']
            return float(total or 0)
        return 0.0

class AdminUserEditSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования пользователя в админке"""
    profile = ProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile")
        # is_staff и is_superuser исключены из полей для редактирования
        
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Обновляем данные пользователя (исключая is_staff и is_superuser)
        for attr, value in validated_data.items():
            if attr not in ['is_staff', 'is_superuser']:  # Дополнительная защита
                setattr(instance, attr, value)
        instance.save()
        
        # Обновляем профиль если есть данные
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance


class DepositCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ("amount_usd","method","details")

    def validate_amount_usd(self, v):
        if v is None or v <= 0:
            raise serializers.ValidationError("Сумма должна быть > 0")
        return v