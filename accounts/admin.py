from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ClientProfile, FreelancerProfile
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil no FreelaMatch", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Perfil no FreelaMatch", {"fields": ("email", "role")}),
    )
    list_display = ("username", "email", "role", "is_staff", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser")


admin.site.register(ClientProfile)
admin.site.register(FreelancerProfile)