from decimal import Decimal, ROUND_DOWN

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import MoneyTransferForm
from .models import CustomUser


def transfer_money(sender, acceptor, amount):
    if sender.balance < amount:
        raise ValidationError(f"У отправителя недостаточно средств.")

    sender.balance -= amount
    acceptor.balance += amount
    sender.save()
    acceptor.save()


def index(request):
    form = MoneyTransferForm(request.POST or None)
    users = CustomUser.objects.exclude(inn="")
    error_message = None

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
            error_message = str(e)

    context = {
        "form": form,
        "users": users,
        "error_message": error_message,
    }
    return render(request, "index.html", context)
