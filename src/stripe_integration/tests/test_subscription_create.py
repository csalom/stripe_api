from decimal import Decimal

import pytest
from django.utils import timezone
from model_bakery import baker

from stripe_integration.actions.subscription_create import SubscriptionCreate
from stripe_integration.models import Subscription, PaymentMethod
from stripe_integration.tests.fakers import FakeStripeSubscription, FakerStripePaymentMethod, FakerStripeCustomer, \
    FakerStripePrice


@pytest.mark.django_db
class TestSubscriptionReportCreated:

    def test_subscription_create_payment_method(self, mocker):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        mocker.patch("stripe.PaymentMethod.create", return_value=FakerStripePaymentMethod())

        payment_method, stripe_payment_method = SubscriptionCreate(**data)._create_payment_method()
        assert payment_method.stripe_id == stripe_payment_method.id
        assert payment_method.month == data["month"]
        assert payment_method.year == data["year"]
        assert payment_method.last_digits == data["card_number"][-PaymentMethod.LAST_DIGITS_LENGTH:]

    def test_subscription_create_customer(self, mocker):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }

        stripe_payment_method = FakerStripePaymentMethod()
        payment_method = baker.make(
            'stripe_integration.PaymentMethod',
            last_digits=data["card_number"][-PaymentMethod.LAST_DIGITS_LENGTH:],
            month=data["month"],
            year=data["year"],
            stripe_id=stripe_payment_method.id
        )
        stripe_customer = FakerStripeCustomer()
        mocker.patch("stripe.Customer.create", return_value=stripe_customer)
        customer = SubscriptionCreate(**data)._create_customer(payment_method, stripe_payment_method)
        assert customer.payment_method_id == payment_method.pk
        assert customer.stripe_id == stripe_customer.id
        assert customer.invoice_prefix == stripe_customer.invoice_prefix
        assert customer.full_name == data["full_name"]
        assert customer.email == data["email"]

    def test_subscription_create_subscription(self, mocker):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }

        payment_method = baker.make(
            'stripe_integration.PaymentMethod',
            last_digits=data["card_number"][-PaymentMethod.LAST_DIGITS_LENGTH:],
            month=data["month"],
            year=data["year"]
        )
        customer = baker.make(
            'stripe_integration.Customer',
            payment_method=payment_method,
            full_name=data["full_name"],
            email="john@doe.com",

        )

        stripe_subscription = FakeStripeSubscription(
            sub_id="sub_as23423",
            customer=customer.stripe_id,
            status=Subscription.UNPAID
        )
        mocker.patch("stripe.Subscription.create", return_value=stripe_subscription)
        mocker.patch("stripe.Price.retrieve", return_value=FakerStripePrice(price_id=data["price_id"]))
        subscription = SubscriptionCreate(**data)._create_subscription(customer)
        assert subscription.customer_id == customer.pk
        assert subscription.stripe_id == stripe_subscription.id
        assert subscription.price_id == data["price_id"]
        assert subscription.status == Subscription.UNPAID
        assert subscription.amount == Decimal(100)

    def test_subscription_create_process(self, mocker):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }

        mocker.patch("stripe.PaymentMethod.create", return_value=FakerStripePaymentMethod())
        stripe_customer = FakerStripeCustomer()
        mocker.patch("stripe.Customer.create", return_value=stripe_customer)
        stripe_subscription = FakeStripeSubscription(
            sub_id="sub_as23423",
            customer=stripe_customer.id,
            status=Subscription.UNPAID
        )
        mocker.patch("stripe.Subscription.create", return_value=stripe_subscription)
        mocker.patch("stripe.Price.retrieve", return_value=FakerStripePrice(price_id=data["price_id"]))

        subscription = SubscriptionCreate(**data).process()

        assert subscription.customer.stripe_id == stripe_customer.id
        assert subscription.stripe_id == stripe_subscription.id
        assert subscription.price_id == data["price_id"]
        assert subscription.status == Subscription.UNPAID
        assert subscription.amount == Decimal(100)
