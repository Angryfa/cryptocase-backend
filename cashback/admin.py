from django.contrib import admin
from .models import CashbackSettings, CashbackAccrual, CashbackDebit

@admin.register(CashbackSettings)
class CashbackSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "enabled", "percent", "period_minutes", "run_minute", "updated_at")
    list_editable = ("enabled", "percent", "period_minutes", "run_minute")

@admin.register(CashbackAccrual)
class CashbackAccrualAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount_usd", "percent_used", "slot_started_at", "computed_at", "status")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user",)
    readonly_fields = ("computed_at",)

@admin.register(CashbackDebit)
class CashbackDebitAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount_usd", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)
