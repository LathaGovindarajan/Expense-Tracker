# tracker/views.py

from django.shortcuts import render, redirect
from django.contrib import messages

from .forms  import ProfileForm, CategoryForm, ExpenseForm,SignUpForm,LoginForm
from .models import User, Expense, Category
import datetime



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            if User.objects(username=form.cleaned_data['username']).first():
                messages.error(request, "Username already exists.")
            else:
                User(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password']
                ).save()
                return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = User.objects(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            ).first()
            if user:
                request.session['username'] = user.username
                return redirect('expense_list')
            messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# tracker/views.py

def expense_list(request):
    if 'username' not in request.session:
        return redirect('login')

    user = User.objects(username=request.session['username']).first()
    if not user:
        messages.error(request, "Please log in again.")
        return redirect('login')

    # 1) PROFILE form (salary/alerts)
    if request.method=='POST' and 'salary' in request.POST:
        prof = ProfileForm(request.POST, prefix="prof")
        if prof.is_valid():
            user.salary          = prof.cleaned_data['salary']
            user.spending_goal   = prof.cleaned_data['spending_goal']
            user.alert_threshold = prof.cleaned_data['alert_threshold']
            user.save()
            return redirect('expense_list')
    else:
        prof = ProfileForm(prefix="prof", initial={
            'salary':          user.salary,
            'spending_goal':   user.spending_goal,
            'alert_threshold': user.alert_threshold,
        })

    # 2) EXPENSES and TOTAL
    expenses = Expense.objects(user=user)
    total    = sum(e.amount for e in expenses)
    over_all_alert = (user.alert_threshold > 0 and total > user.alert_threshold)

    # 3) PER‐CATEGORY SPENDING vs GOAL (this month)
    now       = datetime.datetime.utcnow()
    this_month = now.month
    cat_status = []
    for cat in Category.objects:
        spent = sum(
            e.amount
            for e in expenses
            if e.category.id == cat.id and e.date.month == this_month
        )
        cat_status.append({
            'name':  cat.category,
            'goal':  cat.goal,
            'spent': spent,
            'alert': (cat.goal > 0 and spent > cat.goal),
        })

    # 3) Prepare the inline forms
    cat_form = CategoryForm()
    exp_form = ExpenseForm()

    return render(request, 'expense_list.html', {
        'profile_form': prof,
        'over_all_alert': over_all_alert,
        'total': total,
        'cat_status': cat_status,
        'expenses': expenses,
        'cat_form': cat_form,
        'exp_form': exp_form,
    })

def add_category(request):
    if 'username' not in request.session:
        return redirect('login')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            Category(
                category    = form.cleaned_data['category'],
                description = form.cleaned_data['description'],
                goal        = form.cleaned_data['goal']
            ).save()
            return redirect('expense_list')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


def add_expense(request):
    if 'username' not in request.session:
        return redirect('login')
    user = User.objects(username=request.session['username']).first()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            cat = Category.objects(id=form.cleaned_data['category']).first()
            Expense(
                user        = user,
                category    = cat,
                amount      = form.cleaned_data['amount'],
                description = form.cleaned_data['description'],
                date        = form.cleaned_data['date'],
            ).save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect('login')
