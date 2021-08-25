import pytest
from django.utils import timezone
from django.utils.functional import cached_property
from model_bakery import baker
from rest_framework.authtoken.admin import User
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from stripe_integration.models import PaymentMethod
from stripe_integration.tests.fakers import FakeStripeEvent


class ApiTestMixin:

    api_client_cls = APIClient

    @cached_property
    def client(self):
        client = self.api_client_cls()
        client.force_authenticate(user=self.user)
        return client

    @cached_property
    def user(self):
        """
        :return: User for authenticated requests, override for custom needs.
        """
        return User.objects.create(username='test')


@pytest.mark.django_db
class TestCreateSubscriptionView(ApiTestMixin):

    def test_create_subscription_view(self, mocker):
        data = {
            "full_name": "John Doe",
            "email": "john2@doe.com",
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
        subscription = baker.make(
            'stripe_integration.Subscription',
            customer=customer,
            price_id=data["price_id"]
        )

        mocker.patch("stripe_integration.views.CreateSubscriptionView._retrieve_instance", return_value=subscription)
        mocker.patch("stripe_integration.views.CreateSubscriptionView.perform_create")

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

        response = self.client.post("/stripe/subscription/", data=data)
        assert response.status_code == HTTP_201_CREATED
        assert response.data == expected_data

    def test_create_subscription_view_invalid_data(self):
        data = {
            "full_name": "John Doe",
            "email": "john2@doe.com",
            "card_number": "42424242424AA242",
            "month": timezone.now().month - 3,
            "year": timezone.now().year - 1,
            "cvc": 123,
            "price_id": "price_al89kj3sdh45dds"
        }
        response = self.client.post("/stripe/subscription/", data=data)
        assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestStripeWebHook(ApiTestMixin):

    def test_stripe_webhook_bad_request(self, mocker):
        mocker.patch("stripe_integration.views.StripeWebHookView._retrieve_stripe_event",
                     side_effect=ValueError())

        response = self.client.post("/stripe/webhook/", data={})
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_stripe_webhook_subscription_created(self, mocker):
        mocker.patch("stripe_integration.views.StripeWebHookView._retrieve_stripe_event",
                     return_value=FakeStripeEvent(event_type="customer.subscription.created"))
        mocker.patch("stripe_integration.actions.subscription_report_created.SubscriptionReportCreated.process",
                     return_value=True)

        response = self.client.post("/stripe/webhook/", data={})
        assert response.status_code == HTTP_200_OK

    def test_stripe_webhook_subscription_created_not_found(self, mocker):
        mocker.patch("stripe_integration.views.StripeWebHookView._retrieve_stripe_event",
                     return_value=FakeStripeEvent(event_type="customer.subscription.created"))
        mocker.patch("stripe_integration.actions.subscription_report_created.SubscriptionReportCreated.process",
                     return_value=False)

        response = self.client.post("/stripe/webhook/", data={})
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_stripe_webhook_subscription_updated(self, mocker):
        mocker.patch("stripe_integration.views.StripeWebHookView._retrieve_stripe_event",
                     return_value=FakeStripeEvent(event_type="customer.subscription.updated"))
        mocker.patch("stripe_integration.actions.subscription_report_updated.SubscriptionReportUpdated.process",
                     return_value=True)

        response = self.client.post("/stripe/webhook/", data={})
        assert response.status_code == HTTP_200_OK

    def test_stripe_webhook_subscription_updated_not_found(self, mocker):
        mocker.patch("stripe_integration.views.StripeWebHookView._retrieve_stripe_event",
                     return_value=FakeStripeEvent(event_type="customer.subscription.updated"))
        mocker.patch("stripe_integration.actions.subscription_report_updated.SubscriptionReportUpdated.process",
                     return_value=False)

        response = self.client.post("/stripe/webhook/", data={})
        assert response.status_code == HTTP_404_NOT_FOUND
