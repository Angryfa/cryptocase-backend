from django.contrib import admin
from .models import ReferralProfile, ReferralLevelConfig, ReferralBonus

@admin.register(ReferralProfile)
class ReferralProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "code", "referred_by", "referred_at")
    search_fields = ("user__username", "user__email", "code", "referred_by__username", "referred_by__email")
    autocomplete_fields = ("user", "referred_by")


@admin.register(ReferralLevelConfig)
class ReferralLevelConfigAdmin(admin.ModelAdmin):
    list_display = ("id", "level", "percent")
    list_editable = ("percent",)
    ordering = ("level",)

@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "level", "referrer", "referral", "deposit", "percent", "amount_usd")
    list_filter = ("level", "created_at")
    search_fields = ("referrer__email", "referral__email")
    autocomplete_fields = ("referrer", "referral", "deposit")
    ordering = ("-id",)