# tracker/views.py

import datetime
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import SignUpForm, LoginForm, ProfileForm, CategoryForm, ExpenseForm, CategoryGoalForm
from .models import User, Expense, Category


def get_user(request):
    username = request.session.get('username')
    return User.objects(username=username).first() if username else None


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not get_user(request):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def signup_view(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if User.objects(username=form.cleaned_data['username']).first():
            messages.error(request, "Username already exists.")
        else:
            User(**form.cleaned_data).save()
            return redirect('login')
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects(**form.cleaned_data).first()
        if user:
            request.session['username'] = user.username
            return redirect('expense_list')
        messages.error(request, "Invalid credentials")
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect('login')


@login_required
def edit_profile(request):
    user = get_user(request)
    form = ProfileForm(request.POST or None, initial={
        'salary': user.salary,
        'spending_goal': user.spending_goal,
        'alert_threshold': user.alert_threshold,
    })
    if request.method == 'POST' and form.is_valid():
        for field in ['salary', 'spending_goal', 'alert_threshold']:
            setattr(user, field, form.cleaned_data[field])
        user.save()
        return redirect('expense_list')
    return render(request, 'profile_settings.html', {'form': form})


@login_required
def expense_list(request):
    user = get_user(request)
    expenses = Expense.objects(user=user)
    total = sum(e.amount for e in expenses)
    now_month = datetime.datetime.utcnow().month

    editing_id = request.GET.get('edit_goal')
    goal_form = CategoryGoalForm(request.POST or None)
    if request.method == 'POST' and editing_id and goal_form.is_valid():
        category = Category.objects(id=editing_id).first()
        if category:
            category.goal = goal_form.cleaned_data['goal']
            category.save()
        return redirect('expense_list')

    category_status = []
    for cat in Category.objects:
        spent = sum(e.amount for e in expenses if e.category.id == cat.id and e.date.month == now_month)
        category_status.append({
            'obj': cat,
            'goal': cat.goal,
            'spent': spent,
            'alert': cat.goal and spent > cat.goal,
            'editing': editing_id == str(cat.id),
        })

    return render(request, 'expense_list.html', {
        'user': user,
        'expenses': expenses,
        'total': total,
        'over_all_alert': user.alert_threshold and total > user.alert_threshold,
        'category_status': category_status,
        'goal_form': goal_form,
    })


@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Category(**form.cleaned_data).save()
        return redirect('expense_list')
    return render(request, 'add_category.html', {'form': form})


@login_required
def add_expense(request):
    user = get_user(request)
    form = ExpenseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        category = Category.objects(id=form.cleaned_data['category']).first()
        Expense(
            user=user,
            category=category,
            amount=form.cleaned_data['amount'],
            description=form.cleaned_data['description'],
            date=form.cleaned_data['date'],
        ).save()
        return redirect('expense_list')
    return render(request, 'add_expense.html', {'form': form})
