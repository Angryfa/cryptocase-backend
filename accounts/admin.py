from django.contrib import admin
from .models import Profile
from .models import Profile, Withdrawal, WithdrawalStatus


@admin.register(WithdrawalStatus)
class WithdrawalStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ("id","user","amount_usd","status","method","created_at","processed_at")
    list_filter = ("status","method","created_at")
    search_fields = ("user__username","user__email","details","comment")
    autocomplete_fields = ("user","status")
    readonly_fields = ("created_at","processed_at")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id","user","phone","balance_usd","deposit_total_usd","won_total_usd","lost_total_usd","updated_at")
    search_fields = ("user__username","user__email","phone")
    autocomplete_fields = ("user",)
