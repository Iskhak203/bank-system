from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('employees/', views.employee_list, name='employees'),
    path('employees/create/', views.create_employee, name='create_employee'),
    path('employees/edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),

    path('loans/create/', views.create_loan, name='create_loan'),
    path('loans/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('payment/<int:schedule_id>/', views.make_payment, name='make_payment'),

    path('customers/', views.customer_list, name='customers'),
    path('loans/', views.loans_list, name='loans'),
]
