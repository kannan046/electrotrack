from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "site_location")}),
    )
    list_display = ("username", "email", "role",  "site_location", "is_active")  # ✅ Add here
