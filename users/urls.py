from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
]
