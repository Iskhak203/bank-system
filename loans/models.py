from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Employee(models.Model):
    """Банк кызматкери"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    is_active_employee = models.BooleanField(default=True, verbose_name="Активдүү")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Customer(models.Model):
    """Кардар"""
    full_name = models.CharField(max_length=200, verbose_name="Толук аты-жөнү")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    passport_number = models.CharField(max_length=50, verbose_name="Паспорт номери")
    address = models.TextField(verbose_name="Адрес")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, verbose_name="Түзгөн кызматкер")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name


class Loan(models.Model):
    """Кредит"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Кардар")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Берген кызматкер")
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Жалгыз сумма")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name="Процент (%)")
    months = models.IntegerField(default=10, verbose_name="Айлар саны")
    
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Айлык төлөм")
    total_with_interest = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Процент менен жалпы")
    
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Калган сумма")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Активдүү'),
            ('completed', 'Жабылган'),
            ('overdue', 'Мөөнөтү өткөн')
        ],
        default='active',
        verbose_name="Статус"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=timezone.now, verbose_name="Башталган күнү")
    
    def save(self, *args, **kwargs):
        # Автоматтык эсептөө
        if not self.monthly_payment:
            interest_amount = (self.total_amount * self.interest_rate) / 100
            self.total_with_interest = self.total_amount + interest_amount
            self.monthly_payment = self.total_with_interest / self.months
            self.remaining_amount = self.total_with_interest
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Кредит #{self.id} - {self.customer.full_name}"


class PaymentSchedule(models.Model):
    """Төлөм графиги"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='schedules', verbose_name="Кредит")
    month_number = models.IntegerField(verbose_name="Ай номери")
    due_date = models.DateField(verbose_name="Төлөө күнү")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    is_paid = models.BooleanField(default=False, verbose_name="Төлөнгөн")
    paid_date = models.DateTimeField(null=True, blank=True, verbose_name="Төлөнгөн күнү")
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Төлөнгөн сумма")
    
    class Meta:
        ordering = ['month_number']
    
    def __str__(self):
        status = "✓ Төлөнгөн" if self.is_paid else "⏳ Күтүлүүдө"
        return f"Ай {self.month_number} - {self.amount} - {status}"