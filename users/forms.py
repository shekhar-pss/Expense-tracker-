from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator

from .models import Profile

User = get_user_model()

phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message="Enter a valid phone number (7-15 digits, optional leading +)."
)


class BootstrapFormMixin:
    """Adds Bootstrap 5 form-control classes to every field automatically."""

    def _style_fields(self):
        for name, field in self.fields.items():
            css = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + css).strip()


class RegisterForm(BootstrapFormMixin, forms.Form):
    name = forms.CharField(max_length=150, label='Full Name')
    email = forms.EmailField(label='Email Address')
    phone = forms.CharField(max_length=20, label='Phone Number', validators=[phone_validator])
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm = cleaned.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(BootstrapFormMixin, forms.Form):
    username = forms.CharField(label='Email or Phone Number')
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, initial=True, label='Remember Me')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ForgotPasswordForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField(label='Registered Email Address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    name = forms.CharField(max_length=150, label='Full Name')

    class Meta:
        model = Profile
        fields = ['phone', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['name'].initial = self.instance.user.get_full_name() or self.instance.user.username
        self._style_fields()


class SettingsForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['currency', 'dark_mode', 'monthly_budget', 'notifications_enabled']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class StyledPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
