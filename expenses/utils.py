import csv
import io
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone


def apply_date_filter(queryset, filter_key, custom_start=None, custom_end=None):
    """Apply a named quick date-range filter to an Expense queryset."""
    today = timezone.localdate()

    if filter_key == 'today':
        return queryset.filter(date=today)
    if filter_key == 'yesterday':
        return queryset.filter(date=today - timedelta(days=1))
    if filter_key == 'last_7_days':
        return queryset.filter(date__gte=today - timedelta(days=6), date__lte=today)
    if filter_key == 'last_30_days':
        return queryset.filter(date__gte=today - timedelta(days=29), date__lte=today)
    if filter_key == 'this_month':
        return queryset.filter(date__year=today.year, date__month=today.month)
    if filter_key == 'previous_month':
        first_of_month = today.replace(day=1)
        last_month_end = first_of_month - timedelta(days=1)
        return queryset.filter(date__year=last_month_end.year, date__month=last_month_end.month)
    if filter_key == 'this_year':
        return queryset.filter(date__year=today.year)
    if filter_key == 'custom' and custom_start and custom_end:
        return queryset.filter(date__gte=custom_start, date__lte=custom_end)
    return queryset


def export_expenses_csv(expenses, filename='expenseflow_report.csv'):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Title', 'Category', 'Payment Method', 'Amount', 'Description'])
    for e in expenses:
        writer.writerow([
            e.date.strftime('%Y-%m-%d'), e.title, e.category.name,
            e.get_payment_method_display(), str(e.amount), e.description
        ])
    return response


def export_expenses_pdf(expenses, title='ExpenseFlow Report', filename='expenseflow_report.pdf'):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title, styles['Title']), Spacer(1, 12)]

    data = [['Date', 'Title', 'Category', 'Payment', 'Amount']]
    total = 0
    for e in expenses:
        data.append([e.date.strftime('%Y-%m-%d'), e.title, e.category.name, e.get_payment_method_display(), f"{e.amount:.2f}"])
        total += float(e.amount)
    data.append(['', '', '', 'Total', f"{total:.2f}"])

    table = Table(data, colWidths=[2.2 * cm, 5 * cm, 3.5 * cm, 3.5 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f3f4f6')]),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
