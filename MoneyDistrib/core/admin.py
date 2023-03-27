from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Класс CustomUserAdmin наследует UserAdmin для настройки
    представления и управления моделью CustomUser в административном
    интерфейсе Django.
    """

    list_display = (
        "username",
        "email",
        "inn",
        "balance",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "inn", "balance")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "inn",
                    "balance",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    search_fields = (
        "username",
        "email",
        "inn",
    )
    ordering = ("username",)
