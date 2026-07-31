from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'currency', 'monthly_budget', 'dark_mode', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('currency', 'dark_mode')
