from decimal import ROUND_DOWN, Decimal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import MoneyTransferForm
from .models import CustomUser


def transfer_money(sender, acceptor, amount):
    """
    Переводит деньги от отправителя к получателю.
    """
    if sender.balance < amount:
        raise ValidationError(f"У отправителя недостаточно средств.")

    sender.balance -= amount
    acceptor.balance += amount
    sender.save()
    acceptor.save()


def index(request):
    """
    Обработчик основного представления приложения. Отображает форму для
    отправки денег, а также список пользователей. В случае успешной отправки
    денег перенаправляет на ту же страницу с сообщением об успешной операции.
    В случае возникновения ошибок, отображает сообщения об ошибках.
    """
    form = MoneyTransferForm(request.POST or None)
    users = CustomUser.objects.exclude(inn="")

    if form.is_valid():
        sender = form.cleaned_data["sender"]
        amount = Decimal(form.cleaned_data["amount"])
        acceptors = form.cleaned_data["inn_list"]

        transfer_amount = (amount / len(acceptors)).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )

        try:
            with transaction.atomic():
                if sender.balance < amount:
                    raise ValidationError(f"У отправителя недостаточно средств.")
                for acceptor in acceptors:
                    transfer_money(sender, acceptor, transfer_amount)
            return redirect("core:index")
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(
                request,
                "Произошла непредвиденная ошибка. Пожалуйста, попробуйте еще раз.",
            )

    context = {
        "form": form,
        "users": users,
    }
    return render(request, "index.html", context)
