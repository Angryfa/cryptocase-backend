from django.contrib import admin
from .models import ReferralProfile, ReferralLevelConfig

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
