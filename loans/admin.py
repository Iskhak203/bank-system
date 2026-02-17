# loans/admin.py
from django.contrib import admin
from .models import Employee, Customer, Loan, PaymentSchedule
from datetime import timedelta


class PaymentScheduleInline(admin.TabularInline):
    model = PaymentSchedule
    extra = 0
    readonly_fields = ['month_number', 'due_date', 'amount', 'is_paid', 'paid_date']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'employee', 'total_amount', 'remaining_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__full_name', 'id']
    inlines = [PaymentScheduleInline]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Автоматтык график түзүү
        if not obj.schedules.exists():
            for i in range(1, obj.months + 1):
                # Ар бир айды кошуу (30 күн деп эсептебейбиз, так айлык)
                from datetime import date
                import calendar
                
                year = obj.start_date.year
                month = obj.start_date.month + i
                
                # Ай 12ден ашса, жылга өткөрүү
                while month > 12:
                    month -= 12
                    year += 1
                
                # Айдын акыркы күнү
                last_day = calendar.monthrange(year, month)[1]
                day = min(obj.start_date.day, last_day)
                
                due_date = date(year, month, day)
                
                PaymentSchedule.objects.create(
                    loan=obj,
                    month_number=i,
                    due_date=due_date,
                    amount=obj.monthly_payment
                )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'passport_number', 'created_by', 'created_at']
    search_fields = ['full_name', 'phone', 'passport_number']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_active_employee', 'created_at']
    list_filter = ['is_active_employee']


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ['loan', 'month_number', 'amount', 'is_paid', 'due_date']
    list_filter = ['is_paid', 'due_date']