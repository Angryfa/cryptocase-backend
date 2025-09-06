from django.contrib import admin
from .models import Profile
from .models import Profile, Withdrawal, WithdrawalStatus, Deposit, DepositStatus
from django.utils import timezone
from django.db import transaction


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

@admin.register(DepositStatus)
class DepositStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")

@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("id","user","amount_usd","status","method","created_at","processed_at")
    list_filter = ("status","method","created_at")
    search_fields = ("user__username","user__email","details","comment")
    autocomplete_fields = ("user","status")
    readonly_fields = ("created_at","processed_at")

    actions = ["approve_deposits","reject_deposits"]

    @admin.action(description="Подтвердить депозит (зачислить на баланс)")
    def approve_deposits(self, request, queryset):
        approved = 0
        with transaction.atomic():
            # блокируем строки депозитов
            for d in queryset.select_for_update().select_related("user", "status"):
                if d.processed_at or d.status.code != "pending":
                    continue
                prof, _ = Profile.objects.get_or_create(user=d.user)
                prof.balance_usd       += d.amount_usd
                prof.save(update_fields=["balance_usd","updated_at"])

                # ставим статус approved
                approved_status = DepositStatus.objects.filter(code="approved").first()
                if approved_status:
                    d.status = approved_status
                d.processed_at = timezone.now()
                d.save(update_fields=["status","processed_at"])
                approved += 1
        self.message_user(request, f"Подтверждено депозитов: {approved}")

    @admin.action(description="Отклонить депозит")
    def reject_deposits(self, request, queryset):
        with transaction.atomic():
            for d in queryset.select_for_update().select_related("status"):
                if d.processed_at or d.status.code != "pending":
                    continue
                rejected_status = DepositStatus.objects.filter(code="rejected").first()
                if rejected_status:
                    d.status = rejected_status
                d.processed_at = timezone.now()
                d.save(update_fields=["status","processed_at"])
        self.message_user(request, "Отклонено")