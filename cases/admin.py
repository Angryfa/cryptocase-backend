from django.contrib import admin
from .models import Prize, CaseType, Case, CasePrize, Spin
from django.utils.html import format_html

@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image_preview", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    readonly_fields = ("image_preview", "created_at", "updated_at")
    list_per_page = 20

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Изображение"

@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "name", "is_limited", "is_timed", "sort_order", "is_active")
    list_filter = ("is_active", "is_limited", "is_timed")
    search_fields = ("type", "name")

class CasePrizeInline(admin.TabularInline):
    model = CasePrize
    extra = 1
    fields = ("prize", "amount_min_usd", "amount_max_usd", "weight")
    autocomplete_fields = ["prize"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("prize")

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "name", 
        "type", 
        "price_usd", 
        "is_active", 
        "spins_total", 
        "spins_used", 
        "spins_remaining",
        "avatar_preview",   # новое поле для списка
    )
    list_filter = ("is_active", "type")
    search_fields = ("name",)
    inlines = [CasePrizeInline]
    readonly_fields = ("avatar_preview",)  # превью только для отображения

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />', obj.avatar.url)
        return "—"
    avatar_preview.short_description = "Аватар"

@admin.register(CasePrize)
class CasePrizeAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "prize", "amount_min_usd", "amount_max_usd", "weight")
    list_filter = ("case", "prize")
    search_fields = ("prize__name", "case__name")

@admin.register(Spin)
class SpinAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "prize_name", "amount_display", "created_at")
    list_filter = ("case", "created_at")
    search_fields = ("case__name", "case_prize__prize__name")
    
    def prize_name(self, obj):
        if obj.case_prize and obj.case_prize.prize:
            return obj.case_prize.prize.name
        elif obj.prize:
            return obj.prize.prize_name
        return "Неизвестный приз"
    prize_name.short_description = "Приз"
    
    def amount_display(self, obj):
        if obj.actual_amount_usd:
            return f"${obj.actual_amount_usd}"
        elif obj.prize and obj.prize.amount_usd:
            return f"${obj.prize.amount_usd}"
        return "—"
    amount_display.short_description = "Сумма выигрыша"
