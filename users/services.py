import logging

from django.conf import settings

logger = logging.getLogger("main")


# YOOKASSA PAYMENT
def create_payment(email, amount, user, request):
    from django.conf import settings
    from yookassa import Configuration, Payment

    # Ключи доступа
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    # Объект платежа
    payment = Payment.create(
        {
            "amount": {"value": str(amount), "currency": "RUB"},
            "payment_method_data": {"type": "bank_card"},
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YOOKASSA_REDIRECT_URL,
            },
            "capture": True,
            "description": f"Платеж для пользователя {email}",
            "metadata": {"userId": str(user.id)},
        }
    )
    return payment.confirmation.confirmation_url


def user_change_balance(user_id, notification):
    from users.models import User

    user = User.objects.get(id=user_id)

    user.balance += notification.object.payment.amount.value
    user.save()
