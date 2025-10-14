from django.contrib import admin
from .models import Promocode, PromocodeActivation


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "code", "promo_type", "amount_usd", "max_activations",
        "remaining_activations", "is_active", "starts_at", "ends_at", "created_at"
    )
    list_filter = ("promo_type", "is_active")
    search_fields = ("code",)
    ordering = ("-created_at", "-id")
    readonly_fields = ("created_at", "updated_at",)


@admin.register(PromocodeActivation)
class PromocodeActivationAdmin(admin.ModelAdmin):
    list_display = ("id", "promocode", "user", "amount_usd", "created_at")
    list_filter = ("promocode",)
    search_fields = ("promocode__code", "user__email", "user__username")
    ordering = ("-created_at", "-id")
