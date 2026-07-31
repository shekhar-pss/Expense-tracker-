from django.conf import settings
from django.db import models


class Profile(models.Model):
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee (₹)'),
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')
    dark_mode = models.BooleanField(default=False)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.get_username()}"

    @property
    def currency_symbol(self):
        return {'INR': '₹', 'USD': '$', 'EUR': '€'}.get(self.currency, '₹')
