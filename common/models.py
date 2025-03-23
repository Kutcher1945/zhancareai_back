from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password, make_password

class User(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Пациент'),
        ('doctor', 'Доктор'),
        ('admin', 'Администратор'),
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="Телефон")
    password = models.CharField(max_length=255, verbose_name="Пароль")  # ✅ Must store hashed passwords!
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Фамилия")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='patient', verbose_name="Роль")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def set_password(self, raw_password):
        """Hashes and saves the password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the password"""
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        """Custom property to check authentication status"""
        return True  # ✅ Always return True if a user instance exists

    def __str__(self):
        return f"{self.email} - {self.get_role_display()}"

    class Meta:
        db_table = "common_users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        # Add any other options or constraints you need

class CustomToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True, default=Token.generate_key, editable=False)
    user = models.OneToOneField(
        User, 
        related_name='auth_token', 
        on_delete=models.CASCADE, 
        verbose_name="User"
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        db_table = "common_authtoken"
        verbose_name = "Токен"
        verbose_name_plural = "Токены"

    def __str__(self):
        return self.key

class Company(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'common_companies'
        verbose_name = "Компания"
        verbose_name_plural = "Компании"


# class Consultation(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Ожидание"),
#         ("ongoing", "В процессе"),
#         ("completed", "Завершено"),
#         ("cancelled", "Отменено"),
#     ]

#     patient = models.ForeignKey(
#         "User", on_delete=models.CASCADE, related_name="consultations_as_patient", verbose_name="Пациент"
#     )
#     doctor = models.ForeignKey(
#         "User", on_delete=models.CASCADE, related_name="consultations_as_doctor", verbose_name="Доктор"
#     )
#     meeting_id = models.CharField(max_length=255, unique=True, verbose_name="ID Видеозвонка")
#     status = models.CharField(
#         max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
#     )
#     started_at = models.DateTimeField(null=True, blank=True, verbose_name="Время начала")
#     ended_at = models.DateTimeField(null=True, blank=True, verbose_name="Время завершения")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

#     def start(self):
#         """Marks consultation as ongoing and sets start time."""
#         self.status = "ongoing"
#         self.started_at = timezone.now()
#         self.save()

#     def end(self):
#         """Marks consultation as completed and sets end time."""
#         self.status = "completed"
#         self.ended_at = timezone.now()
#         self.save()

#     def __str__(self):
#         return f"Видеозвонок {self.patient} с {self.doctor} - {self.get_status_display()}"

#     class Meta:
#         db_table = "consultations"
#         verbose_name = "Консультация"
#         verbose_name_plural = "Консультации"