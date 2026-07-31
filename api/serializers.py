from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import serializers

from expenses.models import Expense, Category
from users.models import Profile

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_phone(self, value):
        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return value

    def create(self, validated_data):
        name_parts = validated_data['name'].strip().split(' ', 1)
        username = validated_data['email'].split('@')[0]
        base_username, counter = username, 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else '',
            password=validated_data['password'],
        )
        Profile.objects.filter(user=user).update(phone=validated_data['phone'])
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_default']
        read_only_fields = ['is_default']


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'amount', 'category', 'category_name', 'date',
            'payment_method', 'payment_method_display', 'description', 'notes',
            'receipt', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    total_expenses = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'name', 'email', 'phone', 'avatar', 'currency', 'dark_mode',
            'monthly_budget', 'notifications_enabled', 'total_expenses', 'created_at',
        ]

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_total_expenses(self, obj):
        return Expense.objects.filter(user=obj.user).aggregate(total=Sum('amount'))['total'] or 0
