import json
from datetime import date

from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

from expenses.models import Expense, Category
from .forms import (
    RegisterForm, LoginForm, ForgotPasswordForm, ProfileUpdateForm,
    SettingsForm, StyledPasswordChangeForm,
)
from .models import Profile

User = get_user_model()


def welcome(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')
    return render(request, 'welcome.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            name_parts = data['name'].strip().split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            username = data['email'].split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=data['email'],
                first_name=first_name,
                last_name=last_name,
                password=data['password'],
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = data['phone']
            profile.save()

            messages.success(request, "Account created successfully! Please log in.")
            return redirect('users:login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'expenses:dashboard'
                return redirect(next_url)
            messages.error(request, "Invalid credentials. Please check your email/phone and password.")
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('users:welcome')


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email__iexact=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(
                    reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                send_mail(
                    subject='Reset your ExpenseFlow password',
                    message=f'Click the link to reset your password: {reset_url}',
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=True,
                )
            messages.success(request, "If that email exists in our system, a reset link has been sent.")
            return redirect('users:login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'registration/forgot_password.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid_link = user is not None and default_token_generator.check_token(user, token)

    if valid_link and request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if not password or len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful. Please log in.")
            return redirect('users:login')

    return render(request, 'registration/password_reset_confirm.html', {'valid_link': valid_link})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    total_expenses = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    total_categories = Category.objects.filter(user=request.user).count() + Category.objects.filter(user__isnull=True).count()
    today = timezone.localdate()
    monthly_spending = Expense.objects.filter(
        user=request.user, date__year=today.year, date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            name = form.cleaned_data['name'].strip().split(' ', 1)
            request.user.first_name = name[0]
            request.user.last_name = name[1] if len(name) > 1 else ''
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'total_expenses': total_expenses,
        'total_categories': total_categories,
        'monthly_spending': monthly_spending,
    }
    return render(request, 'users/profile.html', context)


@login_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'save_settings' in request.POST:
            form = SettingsForm(request.POST, instance=profile)
            password_form = StyledPasswordChangeForm(user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Settings updated successfully.")
                return redirect('users:settings')
        elif 'change_password' in request.POST:
            form = SettingsForm(instance=profile)
            password_form = StyledPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect('users:settings')
    else:
        form = SettingsForm(instance=profile)
        password_form = StyledPasswordChangeForm(user=request.user)

    return render(request, 'users/settings.html', {'form': form, 'password_form': password_form, 'profile': profile})


@login_required
@require_POST
def toggle_dark_mode(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        payload = {}
    profile.dark_mode = bool(payload.get('dark_mode', not profile.dark_mode))
    profile.save(update_fields=['dark_mode'])
    return JsonResponse({'success': True, 'dark_mode': profile.dark_mode})


@login_required
@require_POST
def toggle_dark_mode(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        data = {}
    profile.dark_mode = bool(data.get('dark_mode', not profile.dark_mode))
    profile.save(update_fields=['dark_mode'])
    return JsonResponse({'dark_mode': profile.dark_mode})
