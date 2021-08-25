import logging
import stripe

from django.conf import settings
from django.db import transaction

from stripe_integration.actions.utils import price_amount
from stripe_integration.models import PaymentMethod, Customer, Subscription


logger = logging.getLogger(__name__)


class SubscriptionCreate:
    """
    Class to create a subscription to stripe and register the data on the DB.
    This class has to be used with validated data.

    We're assuming that the application only allows to pay with a credit/debit card.

    The process of stripe suscription will be done on the process method, which steps are:
    - Create payment method on stripe and register to DB, saving the stripe ID
    - Create customer on stripe and register to DB, saving the stripe ID
    - Attach customer to stripe payment method
    - With stripe price id, retrieve price information to fetch the amount of the subscruption plan
    - Create subscription on stripe and register to DB as unpaid (waiting to webhook notification), saving the stripe ID

    """

    stripe.api_key = settings.STRIPE_API_KEY

    full_name = None
    email = None
    last_digits = None
    month = None
    year = None
    cvc = None
    price_id = None

    def __init__(self, full_name, email, card_number, month, year, cvc, price_id) -> None:
        super().__init__()

        self.full_name = full_name
        self.email = email
        self.card_number = card_number
        self.last_digits = card_number[-PaymentMethod.LAST_DIGITS_LENGTH:]
        self.month = month
        self.year = year
        self.cvc = cvc
        self.price_id = price_id

    def process(self):
        with transaction.atomic():
            payment_method, stripe_payment_method = self._create_payment_method()
            logger.info(f"PaymentMethod {payment_method.stripe_id} created")
            customer = self._create_customer(payment_method, stripe_payment_method)
            logger.info(f"Customer {customer.stripe_id} created")
            subscription = self._create_subscription(customer)
            logger.info(f"Subscription {subscription.stripe_id} created")
            return subscription

    def _create_payment_method(self):
        payment_method_data = {
            "type": "card",
            "card": {
                "number": self.card_number,
                "exp_month": self.month,
                "exp_year": self.year,
                "cvc": self.cvc
            }
        }
        stripe_payment_method = stripe.PaymentMethod.create(**payment_method_data)

        return PaymentMethod.objects.create(
            stripe_id=stripe_payment_method.id,
            last_digits=self.last_digits,
            month=self.month,
            year=self.year,
        ), stripe_payment_method

    def _create_customer(self, payment_method, stripe_payment_method):
        stripe_customer = stripe.Customer.create(
            payment_method=payment_method.stripe_id,
            invoice_settings={"default_payment_method": payment_method.stripe_id},
            name=self.full_name,
            email=self.email,
        )
        stripe_payment_method.attach(customer=stripe_customer.id)

        return Customer.objects.create(
            stripe_id=stripe_customer.id,
            invoice_prefix=stripe_customer.invoice_prefix,
            full_name=self.full_name,
            email=self.email,
            payment_method=payment_method,
        )

    def _create_subscription(self, customer):
        stripe_price = stripe.Price.retrieve(id=self.price_id)
        stripe_subscription = stripe.Subscription.create(
            customer=customer.stripe_id,
            items=[{"price": self.price_id}]
        )

        return Subscription.objects.create(
            stripe_id=stripe_subscription.id,
            price_id=self.price_id,
            customer=customer,
            status=Subscription.UNPAID,
            amount=price_amount(stripe_price.unit_amount),
        )
