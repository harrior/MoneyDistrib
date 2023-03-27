from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser


class MoneyTransferForm(forms.Form):
    """
    Класс MoneyTransferForm представляет собой форму для осуществления
    денежных переводов между пользователями на основе CustomUser модели.
    """

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
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": 0.01, "min": 0}
        ),
    )

    def clean_inn_list(self):
        """
        Метод clean_inn_list проверяет валидность и уникальность ИНН в списке
        получателей и возвращает список объектов CustomUser, соответствующих ИНН.
        """
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

        return list(CustomUser.objects.filter(inn__in=inns))

    def clean(self):
        """
        Метод clean проверяет корректность данных формы, включая сумму перевода,
        отправителя и получателей.
        """
        cleaned_data = super().clean()

        sender = cleaned_data.get("sender")
        inn_list = cleaned_data.get("inn_list")
        amount = cleaned_data.get("amount")

        if not isinstance(sender, CustomUser):
            raise ValidationError(f"Отправителя с таким id нет в системе")

        if not inn_list:
            raise ValidationError(f"Список ИНН содержит ошибки")

        if not all(map(lambda inn: isinstance(inn, CustomUser), inn_list)):
            raise ValidationError(f"Список ИНН содержит ошибки")

        if sender in inn_list:
            raise ValidationError(f"Нельзя отправить деньги самому себе")

        if amount < 0 or amount is None:
            raise ValidationError(f"Сумма должна быть положительной.")

        if amount > sender.balance:
            raise ValidationError(f"У отправителя недостаточно средств.")


def is_valid_inn(inn):
    """
    Функция is_valid_inn проверяет валидность ИНН на основе его длины и состава.
    """
    return inn.isdigit() and 10 <= len(inn) <= 12
