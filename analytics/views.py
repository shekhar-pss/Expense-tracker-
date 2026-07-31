import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Max, Min, Count
from django.shortcuts import render
from django.utils import timezone

from expenses.models import Expense


@login_required
def analytics_view(request):
    user = request.user
    today = timezone.localdate()
    expenses = Expense.objects.filter(user=user)

    stats = expenses.aggregate(
        average=Avg('amount'), largest=Max('amount'), smallest=Min('amount'), count=Count('id')
    )

    most_used_category = (
        expenses.values('category__name').annotate(count=Count('id')).order_by('-count').first()
    )

    # Category distribution (all-time)
    category_qs = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
    category_labels = [c['category__name'] for c in category_qs]
    category_data = [float(c['total']) for c in category_qs]

    # Payment method distribution
    payment_qs = expenses.values('payment_method').annotate(total=Sum('amount')).order_by('-total')
    payment_labels = [dict(Expense.PAYMENT_METHOD_CHOICES).get(p['payment_method'], p['payment_method']) for p in payment_qs]
    payment_data = [float(p['total']) for p in payment_qs]

    # Expense timeline - last 30 days
    timeline_labels, timeline_data = [], []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_total = expenses.filter(date=day).aggregate(total=Sum('amount'))['total'] or 0
        timeline_labels.append(day.strftime('%d %b'))
        timeline_data.append(float(day_total))

    # Monthly spending - last 12 months
    monthly_labels, monthly_data = [], []
    for i in range(11, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        total = expenses.filter(date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0
        monthly_labels.append(f"{year}-{month:02d}")
        monthly_data.append(float(total))

    # Top 5 categories
    top_categories = list(category_qs[:5])

    context = {
        'stats': stats,
        'most_used_category': most_used_category,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'payment_labels': json.dumps(payment_labels),
        'payment_data': json.dumps(payment_data),
        'timeline_labels': json.dumps(timeline_labels),
        'timeline_data': json.dumps(timeline_data),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),
        'top_categories': top_categories,
    }
    return render(request, 'analytics/index.html', context)
