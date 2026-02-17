# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bank_system.settings')
django.setup()

from django.contrib.auth.models import User
from loans.models import Employee

# Эски болсо өчүр
User.objects.filter(username='Iskhak').delete()

# Жаңы түз
user = User.objects.create_user('Iskhak', password='comp2003')
user.first_name = 'Исхак'
user.last_name = 'Алишер уулу'
user.save()

Employee.objects.create(user=user, phone='+996 708 515 052')

print("✅ Кызматкер ийгиликтүү түзүлдү!")