from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('loan/create/', views.create_loan, name='create_loan'),
    path('loan/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('payment/<int:schedule_id>/', views.make_payment, name='make_payment'),
    path('customers/', views.customer_list, name='customers'),
    path('loans/', views.loans_list, name='loans'),
    # Кызматкерлерди башкаруу
    path('employees/', views.employee_list, name='employees'),
    path('employees/create/', views.create_employee, name='create_employee'),
    path('employees/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),  # ЖАҢЫ
    # Logout
    path('logout/', LogoutView.as_view(next_page='login', http_method_names=['get', 'post']), name='logout'),
]