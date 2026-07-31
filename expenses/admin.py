from django.contrib import admin
from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_default', 'icon')
    list_filter = ('is_default',)
    search_fields = ('name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'amount', 'date', 'payment_method')
    list_filter = ('category', 'payment_method', 'date')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'date'
