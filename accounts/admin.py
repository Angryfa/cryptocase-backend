from django.contrib import admin
from django.utils import timezone
from django.db import transaction
from django.contrib import messages  # ← добавь это

from .models import Profile, Withdrawal, WithdrawalStatus, Deposit, DepositStatus


@admin.register(WithdrawalStatus)
class WithdrawalStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount_usd", "status", "method", "created_at", "processed_at")
    list_filter = ("status", "method", "created_at")
    search_fields = ("user__username", "user__email", "details", "comment")
    autocomplete_fields = ("user", "status")
    readonly_fields = ("created_at", "processed_at")

    # ✅ экшены
    actions = ["approve_withdrawals", "reject_withdrawals", "cancel_withdrawals"]

    @admin.action(description="Подтвердить вывод (списать с баланса)")
    def approve_withdrawals(self, request, queryset):
        ok = WithdrawalStatus.objects.filter(code="approved").first()
        if not ok:
            self.message_user(request, "Нет статуса 'approved' в справочнике.", level=messages.ERROR)
            return

        done, skipped, no_funds = 0, 0, 0
        with transaction.atomic():
            for w in queryset.select_for_update().select_related("user", "status"):
                # берём только PENDING, не обработанные ранее
                if w.processed_at or w.status.code != "pending":
                    skipped += 1
                    continue

                prof, _ = Profile.objects.get_or_create(user=w.user)
                if prof.balance_usd >= w.amount_usd:
                    # списываем и подтверждаем
                    prof.balance_usd -= w.amount_usd
                    prof.save(update_fields=["balance_usd", "updated_at"])

                    w.status = ok
                    w.processed_at = timezone.now()
                    w.save(update_fields=["status", "processed_at"])
                    done += 1
                else:
                    no_funds += 1

        msg = f"Подтверждено: {done}. Пропущено (не PENDING/уже обработаны): {skipped}."
        if no_funds:
            msg += f" Недостаточно средств: {no_funds}."
        self.message_user(request, msg)

    @admin.action(description="Отклонить вывод")
    def reject_withdrawals(self, request, queryset):
        rej = WithdrawalStatus.objects.filter(code="rejected").first()
        if not rej:
            self.message_user(request, "Нет статуса 'rejected' в справочнике.", level=messages.ERROR)
            return

        done, skipped = 0, 0
        with transaction.atomic():
            for w in queryset.select_for_update().select_related("status"):
                if w.processed_at or w.status.code != "pending":
                    skipped += 1
                    continue
                w.status = rej
                w.processed_at = timezone.now()
                w.save(update_fields=["status", "processed_at"])
                done += 1

        self.message_user(request, f"Отклонено: {done}. Пропущено: {skipped}.")

    @admin.action(description="Отменить вывод")
    def cancel_withdrawals(self, request, queryset):
        cnl = WithdrawalStatus.objects.filter(code="cancelled").first()
        if not cnl:
            self.message_user(request, "Нет статуса 'cancelled' в справочнике.", level=messages.ERROR)
            return

        done, skipped = 0, 0
        with transaction.atomic():
            for w in queryset.select_for_update().select_related("status"):
                if w.processed_at or w.status.code != "pending":
                    skipped += 1
                    continue
                w.status = cnl
                w.processed_at = timezone.now()
                w.save(update_fields=["status", "processed_at"])
                done += 1

        self.message_user(request, f"Отменено: {done}. Пропущено: {skipped}.")

    # ✅ если статус меняют вручную в форме — аккуратно проставим processed_at,
    # а при переводе в approved спишем баланс (если хватает).
    def save_model(self, request, obj, form, change):
        if change:
            try:
                old = Withdrawal.objects.get(pk=obj.pk)
            except Withdrawal.DoesNotExist:
                old = None

            if old and old.status_id != obj.status_id:
                # если ставят финальный статус вручную — датируем обработку
                if not obj.processed_at and obj.status.code in {"approved", "rejected", "cancelled"}:
                    obj.processed_at = timezone.now()

                # ручной перевод в approved → попытка списания
                if old.status.code != "approved" and obj.status.code == "approved":
                    prof, _ = Profile.objects.get_or_create(user=obj.user)
                    if prof.balance_usd >= obj.amount_usd:
                        prof.balance_usd -= obj.amount_usd
                        prof.save(update_fields=["balance_usd", "updated_at"])
                    else:
                        self.message_user(
                            request,
                            "Недостаточно средств для списания при переводе в 'approved'. Баланс не изменён.",
                            level=messages.WARNING,
                        )

        super().save_model(request, obj, form, change)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "balance_usd", "deposit_total_usd", "won_total_usd", "lost_total_usd", "updated_at")
    search_fields = ("user__username", "user__email", "phone")
    autocomplete_fields = ("user",)


@admin.register(DepositStatus)
class DepositStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount_usd", "status", "method", "created_at", "processed_at")
    list_filter = ("status", "method", "created_at")
    search_fields = ("user__username", "user__email", "details", "comment")
    autocomplete_fields = ("user", "status")
    readonly_fields = ("created_at", "processed_at")

    actions = ["approve_deposits", "reject_deposits"]

    @admin.action(description="Подтвердить депозит (зачислить на баланс)")
    def approve_deposits(self, request, queryset):
        approved = 0
        with transaction.atomic():
            for d in queryset.select_for_update().select_related("user", "status"):
                if d.processed_at or d.status.code != "pending":
                    continue
                prof, _ = Profile.objects.get_or_create(user=d.user)
                prof.balance_usd += d.amount_usd
                prof.save(update_fields=["balance_usd", "updated_at"])

                approved_status = DepositStatus.objects.filter(code="approved").first()
                if approved_status:
                    d.status = approved_status
                d.processed_at = timezone.now()
                d.save(update_fields=["status", "processed_at"])
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
                d.save(update_fields=["status", "processed_at"])
        self.message_user(request, "Отклонено")
