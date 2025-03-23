from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomToken, Company

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "first_name", "last_name", "is_active", "created_at", "role")
    search_fields = ("email", "phone", "first_name", "last_name")
    list_filter = ("is_active", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(CustomToken)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created")
    search_fields = ("user__email",)
    ordering = ("-created",)
    readonly_fields = ("key", "created")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")


# @admin.register(Consultation)
# class ConsultationAdmin(admin.ModelAdmin):
#     list_display = ("id", "patient", "doctor", "status", "created_at", "started_at", "ended_at")
#     list_filter = ("status", "created_at")
#     search_fields = ("patient__first_name", "doctor__first_name", "meeting_id")
