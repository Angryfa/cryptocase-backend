from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Deposit

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")

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

    class Meta(UserPublicSerializer.Meta):
        fields = UserPublicSerializer.Meta.fields + ("profile",)


class DepositCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = ("amount_usd","method","details")

    def validate_amount_usd(self, v):
        if v is None or v <= 0:
            raise serializers.ValidationError("Сумма должна быть > 0")
        return v