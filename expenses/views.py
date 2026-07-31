import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import ExpenseForm, CategoryForm
from .models import Expense, Category
from .utils import apply_date_filter, export_expenses_csv, export_expenses_pdf


@login_required
def dashboard(request):
    user = request.user
    today = timezone.localdate()
    expenses = Expense.objects.filter(user=user)

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    today_total = expenses.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0
    month_total = expenses.filter(date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0

    week_start = today - timedelta(days=today.weekday())
    week_total = expenses.filter(date__gte=week_start, date__lte=today).aggregate(total=Sum('amount'))['total'] or 0

    top_category = (
        expenses.filter(date__year=today.year, date__month=today.month)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )

    recent_expenses = expenses.select_related('category')[:6]

    profile = getattr(user, 'profile', None)
    budget = profile.monthly_budget if profile else 0
    remaining_balance = (budget - month_total) if budget else None
    budget_exceeded = bool(budget) and month_total > budget

    # Last 6 months trend
    trend_labels, trend_data = [], []
    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        m_total = expenses.filter(date__year=year, date__month=month).aggregate(total=Sum('amount'))['total'] or 0
        trend_labels.append(f"{year}-{month:02d}")
        trend_data.append(float(m_total))

    category_breakdown = (
        expenses.filter(date__year=today.year, date__month=today.month)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = [c['category__name'] for c in category_breakdown]
    category_data = [float(c['total']) for c in category_breakdown]

    context = {
        'total_expenses': total_expenses,
        'today_total': today_total,
        'month_total': month_total,
        'week_total': week_total,
        'top_category': top_category,
        'recent_expenses': recent_expenses,
        'remaining_balance': remaining_balance,
        'budget': budget,
        'budget_exceeded': budget_exceeded,
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
    }
    return render(request, 'dashboard.html', context)


@login_required
def expense_list(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).select_related('category')

    query = request.GET.get('q', '').strip()
    if query:
        expenses = expenses.filter(
            Q(title__icontains=query) | Q(description__icontains=query) |
            Q(category__name__icontains=query) | Q(notes__icontains=query)
        )

    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)

    payment_method = request.GET.get('payment_method')
    if payment_method:
        expenses = expenses.filter(payment_method=payment_method)

    date_filter = request.GET.get('date_filter')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    if date_filter:
        expenses = apply_date_filter(expenses, date_filter, start, end)

    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)

    sort = request.GET.get('sort', '-date')
    allowed_sorts = ['date', '-date', 'amount', '-amount', 'title', '-title', 'category__name', '-category__name']
    if sort in allowed_sorts:
        expenses = expenses.order_by(sort)

    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0

    paginator = Paginator(expenses, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(Q(user=user) | Q(user__isnull=True)).order_by('name')

    params_without_page = request.GET.copy()
    params_without_page.pop('page', None)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'payment_methods': Expense.PAYMENT_METHOD_CHOICES,
        'query': query,
        'total_amount': total_amount,
        'total_count': expenses.count(),
        'current_params': params_without_page.urlencode(),
    }
    return render(request, 'expenses/list.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added successfully.")
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(user=request.user, initial={'date': timezone.localdate()})

    return render(request, 'expenses/form.html', {'form': form, 'mode': 'add'})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully.")
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)

    return render(request, 'expenses/form.html', {'form': form, 'mode': 'edit', 'expense': expense})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, "Expense deleted successfully.")
        return redirect('expenses:expense_list')
    return JsonResponse({'success': False}, status=405)


@login_required
def category_list(request):
    user = request.user
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = user
            category.save()
            messages.success(request, "Category created successfully.")
            return redirect('expenses:category_list')
    else:
        form = CategoryForm(user=user)

    default_categories = Category.objects.filter(user__isnull=True).order_by('name')
    custom_categories = Category.objects.filter(user=user).annotate(expense_count=Count('expenses')).order_by('name')
    default_categories = default_categories.annotate(expense_count=Count('expenses', filter=Q(expenses__user=user)))

    return render(request, 'categories/list.html', {
        'form': form,
        'default_categories': default_categories,
        'custom_categories': custom_categories,
    })


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        if category.expenses.exists():
            messages.error(request, "Cannot delete a category that has expenses. Reassign or delete those expenses first.")
        else:
            category.delete()
            messages.success(request, "Category deleted.")
    return redirect('expenses:category_list')


@login_required
def reports_view(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).select_related('category')

    date_filter = request.GET.get('date_filter', 'this_month')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    expenses = apply_date_filter(expenses, date_filter, start, end)

    export_format = request.GET.get('export')
    if export_format == 'csv':
        return export_expenses_csv(expenses)
    if export_format == 'pdf':
        return export_expenses_pdf(expenses)
    if export_format == 'excel':
        return export_expenses_csv(expenses, filename='expenseflow_report.xls')

    total = expenses.aggregate(total=Sum('amount'), count=Count('id'))
    by_category = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
    by_payment = list(expenses.values('payment_method').annotate(total=Sum('amount')).order_by('-total'))
    payment_display = dict(Expense.PAYMENT_METHOD_CHOICES)
    for row in by_payment:
        row['payment_method_display'] = payment_display.get(row['payment_method'], row['payment_method'])

    context = {
        'expenses': expenses[:100],
        'total': total,
        'by_category': by_category,
        'by_payment': by_payment,
        'date_filter': date_filter,
        'start_date': start or '',
        'end_date': end or '',
    }
    return render(request, 'reports/index.html', context)
