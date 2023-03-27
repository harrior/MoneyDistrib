from django.test import TestCase

from ..forms import MoneyTransferForm
from ..models import CustomUser


class MoneyTransferFormTest(TestCase):
    """
    Тестирование формы MoneyTransferForm.
    """

    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1", password="password", inn="123456789012", balance=100
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", password="password", inn="223456789012", balance=0
        )
        self.user3 = CustomUser.objects.create_user(
            username="user3", password="password", inn="223456123412", balance=0
        )
        self.user4 = CustomUser.objects.create_user(
            username="user4", password="password", inn="212356123412", balance=0
        )

    def test_form_validation(self):
        """
        Тестирование валидации формы MoneyTransferForm.
        """
        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"{self.user2.inn} {self.user3.inn} {self.user4.inn}",
            }
        )
        self.assertTrue(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"{self.user2.inn}",
            }
        )
        self.assertTrue(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": -100500,
                "inn_list": f"{self.user2.inn} {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance * 2,
                "inn_list": f"{self.user2.inn} {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"{self.user1.inn} {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": 100500,
                "amount": 100,
                "inn_list": f"{self.user1.inn} {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"111111111111 {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"111111111111 111111111112",
            }
        )
        self.assertFalse(form.is_valid())

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"",
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_cleaned_data(self):
        """
        Тестирование корректности очищенных данных формы MoneyTransferForm после валидации.
        """
        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"{self.user2.inn} {self.user3.inn} {self.user4.inn}",
            }
        )

        self.assertTrue(form.is_valid())
        form.clean()
        self.assertEqual(form.cleaned_data["sender"], self.user1)
        self.assertEqual(form.cleaned_data["amount"], self.user1.balance)
        self.assertEqual(
            set(form.cleaned_data["inn_list"]),
            set([self.user2, self.user3, self.user4]),
        )

    def test_form_error_messages(self):
        """
        Тестирование сообщений об ошибках в форме MoneyTransferForm.
        """
        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": -100,
                "inn_list": f"{self.user2.inn} {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Сумма должна быть положительной.", form.errors["__all__"])

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance * 2,
                "inn_list": f"{self.user2.inn} {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("У отправителя недостаточно средств.", form.errors["__all__"])

        form = MoneyTransferForm(
            data={
                "sender": self.user1.id,
                "amount": self.user1.balance,
                "inn_list": f"111111111111 {self.user3.inn}",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Список ИНН содержит ошибки", form.errors["__all__"])
