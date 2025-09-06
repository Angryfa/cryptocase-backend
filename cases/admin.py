from django.contrib import admin
from .models import CaseType, Case, CasePrize, Spin

@admin.register(CaseType)
class CaseTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "name", "is_limited", "is_timed", "sort_order", "is_active")
    list_filter = ("is_active", "is_limited", "is_timed")
    search_fields = ("type", "name")

class CasePrizeInline(admin.TabularInline):
    model = CasePrize
    extra = 1

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "price_usd", "is_active", "spins_total", "spins_used", "spins_remaining")
    list_filter = ("is_active", "type")
    search_fields = ("name",)
    inlines = [CasePrizeInline]

@admin.register(CasePrize)
class CasePrizeAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "title", "amount_usd", "weight")
    list_filter = ("case",)
    search_fields = ("title", "case__name")

@admin.register(Spin)
class SpinAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "prize", "created_at")
    list_filter = ("case", "created_at")
