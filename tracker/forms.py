from django import forms
from .models import Category

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.Form):
    salary          = forms.FloatField(label="Monthly Salary", min_value=0)
    spending_goal   = forms.FloatField(label="Spending Goal", min_value=0)
    alert_threshold = forms.FloatField(label="Alert Threshold", min_value=0)

class CategoryGoalForm(forms.Form):
    goal = forms.FloatField(label="Monthly Goal", min_value=0)

class CategoryForm(forms.Form):
    category    = forms.CharField(label="Name", max_length=100)
    description = forms.CharField(label="Description", required=False)
    goal        = forms.FloatField(label="Monthly Goal", min_value=0)

class ExpenseForm(forms.Form):
    category    = forms.ChoiceField(label="Category")
    amount      = forms.FloatField(label="Amount", min_value=0)
    description = forms.CharField(label="Description", required=False)
    date        = forms.DateTimeField(label="Date")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [
            (str(c.id), c.category) for c in Category.objects
        ]