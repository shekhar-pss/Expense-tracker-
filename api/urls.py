from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView, ProfileAPIView, CategoryViewSet, ExpenseViewSet,
    AnalyticsAPIView, ReportsAPIView,
)
from .auth import EmailOrPhoneTokenObtainPairView

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='api-category')
router.register('expenses', ExpenseViewSet, basename='api-expense')

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('login/', EmailOrPhoneTokenObtainPairView.as_view(), name='api-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('profile/', ProfileAPIView.as_view(), name='api-profile'),
    path('analytics/', AnalyticsAPIView.as_view(), name='api-analytics'),
    path('reports/', ReportsAPIView.as_view(), name='api-reports'),
    path('', include(router.urls)),
]
