from django import forms
from django.db.models import Q

from .models import Expense, Category


class ExpenseForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'payment_method', 'description', 'notes', 'receipt']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.TextInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            ).order_by('name')
        for name, field in self.fields.items():
            css = 'form-control'
            if name == 'category' or name == 'payment_method':
                css = 'form-select'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + css).strip()
        self.fields['amount'].widget.attrs['step'] = '0.01'
        self.fields['amount'].widget.attrs['min'] = '0.01'

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Gym Membership'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-heart-pulse (Bootstrap icon)'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Category.objects.filter(Q(user=self.user) | Q(user__isnull=True), name__iexact=name)
        if qs.exists():
            raise forms.ValidationError("This category already exists.")
        return name
