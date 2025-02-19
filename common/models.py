from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password, make_password
import uuid

class User(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="Phone")
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name="Password")
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Last Name")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return self.email

    # def check_password(self, raw_password):
    #     return check_password(raw_password, self.password)
    
    # def save(self, *args, **kwargs):
    #     if self.password and not self.password.startswith("pbkdf2_"):
    #         self.password = make_password(self.password)
    #     super().save(*args, **kwargs)

    class Meta:
        db_table = 'common_users'
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
