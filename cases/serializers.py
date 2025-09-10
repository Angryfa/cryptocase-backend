from rest_framework import serializers
from .models import CaseType, Case, CasePrize, Spin

class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = ("id", "type", "name", "is_limited", "is_timed")

class CasePrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CasePrize
        fields = ("id", "title", "amount_usd", "weight")

class CaseSerializer(serializers.ModelSerializer):
    type = CaseTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        source="type", queryset=CaseType.objects.all(), write_only=True, required=False
    )
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
        )

    def get_is_available_now(self, obj):
        return obj.is_available_now()

class CaseDetailSerializer(CaseSerializer):
    prizes = CasePrizeSerializer(many=True, read_only=True)
    class Meta(CaseSerializer.Meta):
        fields = CaseSerializer.Meta.fields + ("prizes",)

class SpinSerializer(serializers.ModelSerializer):
    prize = CasePrizeSerializer(read_only=True)
    prize_title = serializers.CharField(source="prize.title", read_only=True)
    amount_usd  = serializers.DecimalField(source="prize.amount_usd", max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Spin
        fields = (
            "id", "created_at",
            "case", "prize", "prize_title", "amount_usd",
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
