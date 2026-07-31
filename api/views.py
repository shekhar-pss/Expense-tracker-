from datetime import timedelta

from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from expenses.models import Expense, Category
from users.models import Profile
from .serializers import (
    RegisterSerializer, ExpenseSerializer, CategorySerializer, ProfileSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {'id': user.id, 'email': user.email, 'name': user.get_full_name()},
        }, status=status.HTTP_201_CREATED)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_default']
    search_fields = ['name']

    def get_queryset(self):
        return Category.objects.filter(Q(user=self.request.user) | Q(user__isnull=True)).order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'payment_method', 'date']
    search_fields = ['title', 'description', 'notes', 'category__name']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        expenses = Expense.objects.filter(user=request.user)

        total = expenses.aggregate(total=Sum('amount'))['total'] or 0
        month_total = expenses.filter(date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0
        today_total = expenses.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
        week_start = today - timedelta(days=today.weekday())
        week_total = expenses.filter(date__gte=week_start, date__lte=today).aggregate(total=Sum('amount'))['total'] or 0

        by_category = list(
            expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
        )

        return Response({
            'total_expenses': total,
            'today_total': today_total,
            'week_total': week_total,
            'month_total': month_total,
            'by_category': by_category,
        })


class ReportsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from expenses.utils import apply_date_filter
        expenses = Expense.objects.filter(user=request.user)
        date_filter = request.query_params.get('date_filter', 'this_month')
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')
        expenses = apply_date_filter(expenses, date_filter, start, end)

        serializer = ExpenseSerializer(expenses, many=True)
        total = expenses.aggregate(total=Sum('amount'))['total'] or 0
        return Response({'total': total, 'count': expenses.count(), 'expenses': serializer.data})
