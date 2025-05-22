# tracker/views.py

from django.shortcuts import render, redirect
from django.contrib import messages

from .forms  import ProfileForm, CategoryForm, ExpenseForm,SignUpForm,LoginForm,CategoryGoalForm
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

def logout_view(request):
    request.session.flush()
    return redirect('login')


# tracker/views.py
def edit_profile(request):
    if 'username' not in request.session:
        return redirect('login')
    user = User.objects(username=request.session['username']).first()

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.salary          = form.cleaned_data['salary']
            user.spending_goal   = form.cleaned_data['spending_goal']
            user.alert_threshold = form.cleaned_data['alert_threshold']
            user.save()
            return redirect('expense_list')
    else:
        form = ProfileForm(initial={
            'salary':          user.salary,
            'spending_goal':   user.spending_goal,
            'alert_threshold': user.alert_threshold,
        })
    return render(request, 'profile_settings.html', {'form': form})

# ---------- dashboard ----------
def expense_list(request):
    if 'username' not in request.session:
        return redirect('login')
    user = User.objects(username=request.session['username']).first()

    # ---- per-category goal update ----
    editing_category_id = request.GET.get('edit_goal')
    if request.method == 'POST' and editing_category_id:
        goal_form = CategoryGoalForm(request.POST)
        if goal_form.is_valid():
            category_obj = Category.objects(id=editing_category_id).first()
            if category_obj:
                category_obj.goal = goal_form.cleaned_data['goal']
                category_obj.save()
            return redirect('expense_list')
    else:
        goal_form = CategoryGoalForm()  # blank; will be re-instantiated row-wise

    # ---- compute category status ----
    expenses = Expense.objects(user=user)
    total    = sum(e.amount for e in expenses)

    category_status = []
    now_month = datetime.datetime.utcnow().month

    for category in Category.objects:
        spent = sum(
            e.amount for e in expenses
            if e.category.id == category.id and e.date.month == now_month
        )
        category_status.append({
            'obj':   category,
            'goal':  category.goal,
            'spent': spent,
            'alert': category.goal and spent > category.goal,
            'editing': editing_category_id == str(category.id),
        })

    over_all_alert = user.alert_threshold and total > user.alert_threshold

    return render(request, 'expense_list.html', {
        'user':            user,
        'expenses':        expenses,
        'total':           total,
        'over_all_alert':  over_all_alert,
        'category_status': category_status,
        'goal_form':       goal_form,
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


