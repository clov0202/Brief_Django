from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur
# Register your models here.


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "quartier", "is_staff")
    list_filter = ("role", "quartier", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Informations RueNet", {"fields": ("role", "quartier")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations RueNet", {"fields": ("email", "role", "quartier")}),
    )