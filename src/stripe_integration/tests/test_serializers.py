import pytest
from django.utils import timezone
from model_bakery import baker

from stripe_integration.serializers import (
    CustomerSerializer,
    PaymentMethodSerializer,
    SubscriptionCreateSerializer,
    SubscriptionCreatedSerializer,
)


@pytest.mark.django_db
class TestPaymentMethodSerializer:

    def test_payment_method_serializer(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        serializer = PaymentMethodSerializer(instance=payment_method)
        expected_data = {
            'id': payment_method.id,
            'created_at': payment_method.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'stripe_id': payment_method.stripe_id,
            'last_digits': payment_method.last_digits,
            'month': payment_method.month,
            'year': payment_method.year
        }

        assert serializer.data == expected_data


@pytest.mark.django_db
class TestCustomerSerializer:

    def test_customer_serializer(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        customer = baker.make('stripe_integration.Customer', payment_method=payment_method)
        serializer = CustomerSerializer(instance=customer)
        expected_data = {
            'id': customer.id,
            'created_at': customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'stripe_id': customer.stripe_id,
            'full_name': customer.full_name,
            'email': customer.email,
            'invoice_prefix': customer.invoice_prefix,
            'payment_method': {
                'id': payment_method.id,
                'created_at': payment_method.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'stripe_id': payment_method.stripe_id,
                'last_digits': payment_method.last_digits,
                'month': payment_method.month,
                'year': payment_method.year
            }
        }

        assert serializer.data == expected_data


@pytest.mark.django_db
class TestSubscriptionCreatedSerializer:

    def test_subscription_created_serializer(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        customer = baker.make('stripe_integration.Customer', payment_method=payment_method)
        subscription = baker.make('stripe_integration.Subscription', customer=customer)

        serializer = SubscriptionCreatedSerializer(instance=subscription)

        expected_data = {
            'id': subscription.id,
            'created_at': subscription.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'stripe_id': subscription.stripe_id,
            'price_id': subscription.price_id,
            'status': subscription.status,
            'amount': str(subscription.amount),
            'customer': {
                'id': customer.id,
                'created_at': customer.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'stripe_id': customer.stripe_id,
                'full_name': customer.full_name,
                'email': customer.email,
                'invoice_prefix': customer.invoice_prefix,
                'payment_method': {
                    'id': payment_method.id,
                    'created_at': payment_method.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'stripe_id': payment_method.stripe_id,
                    'last_digits': payment_method.last_digits,
                    'month': payment_method.month,
                    'year': payment_method.year
                }
            }
        }

        assert serializer.data == expected_data


@pytest.mark.django_db
class TestSubscriptionCreateSerializer:

    def test_subscrition_create_serializer_valid(self):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        serializer = SubscriptionCreateSerializer(data=data)
        assert serializer.is_valid(), "Invalid data to SubscriptionCreateSerializer"

    def test_email_exist_validation_error(self, mocker):
        mocker.patch("stripe_integration.serializers.SubscriptionCreateSerializer._email_exists", return_value=True)
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        serializer = SubscriptionCreateSerializer(data=data)
        assert not serializer.is_valid(), "SubscriptionCreateSerializer wrong email validation"

    def test_card_number_validation_error(self):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "424242424242AAAA",
            "month": timezone.now().month,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        serializer = SubscriptionCreateSerializer(data=data)
        assert not serializer.is_valid(), "SubscriptionCreateSerializer wrong card number validation"

    def test_year_validation_error(self):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month,
            "year": timezone.now().year - 1,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        serializer = SubscriptionCreateSerializer(data=data)
        assert not serializer.is_valid(), "SubscriptionCreateSerializer wrong year validation"

    def test_month_validation_error(self):
        data = {
            "full_name": "John Doe",
            "email": "john@doe.com",
            "card_number": "4242424242424242",
            "month": timezone.now().month - 1,
            "year": timezone.now().year,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        serializer = SubscriptionCreateSerializer(data=data)
        assert not serializer.is_valid(), "SubscriptionCreateSerializer wrong month validation"
