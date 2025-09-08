from django.contrib import admin
from .models import Ticket, TicketMessage, TicketStatus


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    fields = ("author", "body", "attachment", "read_by_user_at", "read_by_staff_at", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "user__username", "user__email")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [TicketMessageInline]

    actions = ["close_tickets", "mark_answered"]

    @admin.action(description="Закрыть выбранные тикеты")
    def close_tickets(self, request, queryset):
        updated = queryset.update(status=TicketStatus.CLOSED)
        self.message_user(request, f"Закрыто тикетов: {updated}")

    @admin.action(description="Пометить как отвеченные")
    def mark_answered(self, request, queryset):
        updated = queryset.update(status=TicketStatus.ANSWERED)
        self.message_user(request, f"Отмечено отвеченными: {updated}")


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "author", "created_at", "read_by_user_at", "read_by_staff_at")
    list_filter = ("created_at",)
    search_fields = ("ticket__subject", "author__username", "author__email", "body")
    autocomplete_fields = ("ticket", "author")
    readonly_fields = ("created_at",)


