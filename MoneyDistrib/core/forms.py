from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from .models import CustomUser


class MoneyTransferForm(forms.Form):
    sender = forms.ModelChoiceField(
        queryset=CustomUser.objects.exclude(inn=""),
        label="Отправитель",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    inn_list = forms.CharField(
        label="Список ИНН получателей",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        help_text="Введите ИНН получателей через запятую или пробел",
    )
    amount = forms.DecimalField(
        label="Сумма перевода (на всех получателей)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": 0.01, "min": 0}
        ),
    )

    def clean_inn_list(self):
        inn_list = self.cleaned_data["inn_list"]

        inns = [
            inn.strip() for inn in inn_list.replace(",", " ").split() if inn.strip()
        ]

        for inn in inns:
            if not is_valid_inn(inn):
                raise ValidationError(f"Некорректный ИНН: {inn}")
            if not CustomUser.objects.filter(inn=inn).exists():
                raise ValidationError(f"Пользователь с ИНН {inn} не найден")
            if len(set(inns)) != len(inns):
                raise ValidationError(f"В списке ИНН встречаются дубликаты")

        return CustomUser.objects.filter(inn__in=inns)

    def clean(self):
        cleaned_data = super().clean()

        sender = cleaned_data.get("sender")
        inn_list = cleaned_data.get("inn_list")
        amount = cleaned_data.get("amount")

        if not inn_list:
            raise ValidationError(f"Список ИНН содержит ошибки")

        if sender in inn_list:
            raise ValidationError(f"Нельзя отправить деньги самому себе")

        if amount < 0 or amount is None:
            raise ValidationError(f"Сумма должна быть положительной.")

        if amount > sender.balance:
            raise ValidationError(f"У отправителя недостаточно средств.")


def is_valid_inn(inn):
    return inn.isdigit() and 10 <= len(inn) <= 12
