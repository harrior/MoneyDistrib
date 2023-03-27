from decimal import Decimal
from http import HTTPStatus

from django.db import transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from ..models import CustomUser


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse("core:index")

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

    def test_get_request(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "index.html")

    def test_post_request_success(self):
        data = {
            "sender": self.user1.id,
            "amount": 100,
            "inn_list": f"{self.user2.inn}",
        }
        response = self.client.post(self.index_url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_request_fail(self):
        data = {
            "sender": self.user1.id,
            "amount": self.user1.balance * 2,
            "inn_list": f"{self.user2.inn}",
        }
        response = self.client.post(self.index_url, data)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_money_transfer(self):
        test_cases = [
            {
                "data": {
                    "sender": self.user1.id,
                    "amount": 100,
                    "inn_list": f"{self.user2.inn} {self.user3.inn} {self.user4.inn}",
                },
                "expected_balances": {
                    self.user1: Decimal("0.01"),
                    self.user2: Decimal("33.33"),
                    self.user3: Decimal("33.33"),
                    self.user4: Decimal("33.33"),
                },
            },
            {
                "data": {
                    "sender": self.user2.id,
                    "amount": 33.33,
                    "inn_list": f"{self.user1.inn} {self.user3.inn}",
                },
                "expected_balances": {
                    self.user1: Decimal("16.67"),
                    self.user2: Decimal("0.01"),
                    self.user3: Decimal("49.99"),
                },
            },
        ]

        for case in test_cases:
            with self.subTest(case=case):
                self.client.post(self.index_url, case["data"])

                for user, expected_balance in case["expected_balances"].items():
                    user.refresh_from_db()
                    self.assertEqual(user.balance, expected_balance)

    def test_error_handling(self):
        data = {
            "sender": self.user1.id,
            "amount": -100,
            "inn_list": f"{self.user2.inn} {self.user3.inn}",
        }
        response = self.client.post(self.index_url, data)
        self.assertContains(response, "Сумма должна быть положительной.")

        data = {
            "sender": self.user2.id,
            "amount": 100,
            "inn_list": f"{self.user1.inn} {self.user3.inn}",
        }
        response = self.client.post(self.index_url, data)
        self.assertContains(response, "У отправителя недостаточно средств.")


class MoneyTransferRollbackTest(TransactionTestCase):
    def setUp(self):
        self.client = Client()

        self.index_url = reverse("core:index")

        self.user1 = CustomUser.objects.create_user(
            username="user1", password="password", inn="123456789012", balance=100
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", password="password", inn="223456789012", balance=0
        )
        self.user3 = CustomUser.objects.create_user(
            username="user3", password="password", inn="223456123412", balance=0
        )

    def test_rollback_on_data_change(self):
        def change_data_during_transaction():
            with transaction.atomic():
                self.client.post(
                    self.index_url,
                    {
                        "sender": self.user1.id,
                        "amount": 100,
                        "inn_list": f"{self.user2.inn} {self.user3.inn}",
                    },
                )
                raise ValueError("Simulate error to trigger rollback")

        initial_state = {
            "user1_balance": self.user1.balance,
            "user2_balance": self.user2.balance,
            "user3_balance": self.user3.balance,
        }

        try:
            change_data_during_transaction()
        except ValueError as e:
            self.assertEqual(str(e), "Simulate error to trigger rollback")

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.user3.refresh_from_db()

        self.assertEqual(self.user1.balance, initial_state["user1_balance"])
        self.assertEqual(self.user2.balance, initial_state["user2_balance"])
        self.assertEqual(self.user3.balance, initial_state["user3_balance"])
