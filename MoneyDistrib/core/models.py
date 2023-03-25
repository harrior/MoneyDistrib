from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    inn = models.fields.CharField(
        max_length=12,
        unique=True,
        verbose_name="ИНН",
        help_text="ИНН пользователя",
    )
    balance = models.fields.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Баланс",
        help_text="Текущий остаток по счету",
    )

    def __str__(self):
        return self.username
