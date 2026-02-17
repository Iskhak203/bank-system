from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import Employee, Customer, Loan, PaymentSchedule
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


def is_superuser(user):
    return user.is_superuser


@login_required
def dashboard(request):
    """Негизги панель"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Сиз кызматкер эмессиз!")
        return redirect('logout')
    
    active_loans = Loan.objects.filter(employee=employee, status='active')
    total_given = active_loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_remaining = active_loans.aggregate(Sum('remaining_amount'))['remaining_amount__sum'] or 0
    
    recent_loans = Loan.objects.filter(employee=employee).order_by('-created_at')[:10]
    
    for loan in recent_loans:
        paid_count = loan.schedules.filter(is_paid=True).count()
        if loan.months > 0:
            loan.progress_percent = (paid_count / loan.months) * 100
        else:
            loan.progress_percent = 0
    
    context = {
        'employee': employee,
        'customers_count': Customer.objects.filter(created_by=employee).count(),
        'active_loans_count': active_loans.count(),
        'total_given': total_given,
        'total_remaining': total_remaining,
        'recent_loans': recent_loans,
        'is_superuser': request.user.is_superuser,
    }
    return render(request, 'loans/dashboard.html', context)


# ========== КЫЗМАТКЕРЛЕРДИ БАШКАРУУ ==========

@login_required
@user_passes_test(is_superuser)
def employee_list(request):
    """Бардык кызматкерлерди көрүү"""
    employees = Employee.objects.all().select_related('user')
    return render(request, 'loans/employee_list.html', {'employees': employees})


@login_required
@user_passes_test(is_superuser)
def create_employee(request):
    """Жаңы кызматкер түзүү"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Бул логин ({username}) бар экен!")
            return redirect('create_employee')
        
        user = User.objects.create_user(username=username, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        Employee.objects.create(user=user, phone=phone)
        
        messages.success(request, f"Кызматкер {first_name} {last_name} ийгиликтүү түзүлдү!")
        return redirect('employees')
    
    return render(request, 'loans/create_employee.html')


@login_required
@user_passes_test(is_superuser)
def edit_employee(request, employee_id):
    """Кызматкердин маалыматтарын өзгөртүү (ЖАҢЫ)"""
    employee = get_object_or_404(Employee, id=employee_id)
    user = employee.user
    
    if request.method == 'POST':
        # Маалыматтарды алуу
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        new_password = request.POST.get('new_password')
        is_active = request.POST.get('is_active') == 'on'
        
        # User маалыматтарын жаңыртуу
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = is_active
        
        # Пароль өзгөртүлгөн болсо
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        # Employee маалыматтарын жаңыртуу
        employee.phone = phone
        employee.is_active_employee = is_active
        employee.save()
        
        messages.success(request, f"{first_name} {last_name} маалыматтары жаңыртылды!")
        return redirect('employees')
    
    context = {
        'employee': employee,
        'user': user,
    }
    return render(request, 'loans/edit_employee.html', context)


# ========== БАШКА ФУНКЦИЯЛАР ==========

@login_required
def create_loan(request):
    """Жаңы кредит түзүү"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        messages.error(request, "Сиз кызматкер эмессиз!")
        return redirect('logout')
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
        else:
            customer = Customer.objects.create(
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                passport_number=request.POST.get('passport_number'),
                address=request.POST.get('address'),
                created_by=employee
            )
        
        amount = float(request.POST.get('amount'))
        months = int(request.POST.get('months', 10))
        interest_rate = float(request.POST.get('interest_rate', 10))
        
        loan = Loan.objects.create(
            customer=customer,
            employee=employee,
            total_amount=amount,
            months=months,
            interest_rate=interest_rate
        )
        
        for i in range(1, months + 1):
            due_date = loan.start_date + relativedelta(months=i)
            PaymentSchedule.objects.create(
                loan=loan,
                month_number=i,
                due_date=due_date,
                amount=loan.monthly_payment
            )
        
        messages.success(request, f"Кредит ийгиликтүү түзүлдү! Айлык төлөм: {loan.monthly_payment:.2f} сом")
        return redirect('loan_detail', loan_id=loan.id)
    
    customers = Customer.objects.filter(created_by=employee)
    return render(request, 'loans/create_loan.html', {'customers': customers})


@login_required
def loan_detail(request, loan_id):
    """Кредит деталдары"""
    loan = get_object_or_404(Loan, id=loan_id, employee__user=request.user)
    schedules = loan.schedules.all()
    
    paid_count = schedules.filter(is_paid=True).count()
    total_months = loan.months
    
    if total_months > 0:
        progress_percent = (paid_count / total_months) * 100
    else:
        progress_percent = 0
    
    context = {
        'loan': loan,
        'schedules': schedules,
        'progress_percent': progress_percent,
        'paid_count': paid_count,
        'remaining_count': total_months - paid_count
    }
    return render(request, 'loans/loan_detail.html', context)


@login_required
def make_payment(request, schedule_id):
    """Төлөм жасоо"""
    schedule = get_object_or_404(PaymentSchedule, id=schedule_id, loan__employee__user=request.user)
    
    if request.method == 'POST':
        if not schedule.is_paid:
            schedule.is_paid = True
            schedule.paid_date = datetime.now()
            schedule.paid_amount = schedule.amount
            schedule.save()
            
            loan = schedule.loan
            loan.remaining_amount -= schedule.amount
            if loan.remaining_amount <= 0:
                loan.remaining_amount = 0
                loan.status = 'completed'
            loan.save()
            
            messages.success(request, f"Ай {schedule.month_number} ийгиликтүү төлөндү!")
        else:
            messages.warning(request, "Бул төлөм мурунтан эле төлөнгөн!")
    
    return redirect('loan_detail', loan_id=schedule.loan.id)


@login_required
def customer_list(request):
    """Кардарлар тизмеси"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('logout')
    
    customers = Customer.objects.filter(created_by=employee)
    return render(request, 'loans/customers.html', {'customers': customers})


@login_required
def loans_list(request):
    """Кредиттер тизмеси"""
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('logout')
    
    loans = Loan.objects.filter(employee=employee).order_by('-created_at')
    return render(request, 'loans/loans_list.html', {'loans': loans})