from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Global (default) categories have user=None. Custom categories belong to a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='categories'
    )
    name = models.CharField(max_length=60)
    icon = models.CharField(max_length=40, default='bi-tag', help_text='Bootstrap icon class')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_category_per_user')
        ]

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_CASH = 'cash'
    PAYMENT_UPI = 'upi'
    PAYMENT_CREDIT = 'credit_card'
    PAYMENT_DEBIT = 'debit_card'
    PAYMENT_BANK = 'bank_transfer'

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_UPI, 'UPI'),
        (PAYMENT_CREDIT, 'Credit Card'),
        (PAYMENT_DEBIT, 'Debit Card'),
        (PAYMENT_BANK, 'Bank Transfer'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses')
    date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_CASH)
    description = models.TextField(blank=True)
    notes = models.CharField(max_length=255, blank=True)
    receipt = models.ImageField(upload_to='receipts/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount}"

    def get_absolute_url(self):
        return reverse('expenses:expense_list')
