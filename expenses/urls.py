from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/<int:pk>/edit/', views.edit_expense, name='edit_expense'),
    path('expenses/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('reports/', views.reports_view, name='reports'),
]
