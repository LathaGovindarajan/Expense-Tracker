# tracker/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                views.expense_list,  name='expense_list'),
    path('add/',            views.add_expense,   name='add_expense'),
    path('category/add/',   views.add_category,  name='add_category'),
    path('signup/',         views.signup_view,   name='signup'),
    path('login/',          views.login_view,    name='login'),
    path('logout/',         views.logout_view,   name='logout'),
]
