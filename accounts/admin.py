from django.contrib import admin
from .models import Profile




@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "balance_usd", "deposit_total_usd", "won_total_usd", "lost_total_usd", "updated_at")
    search_fields = ("user__username", "user__email", "phone")
