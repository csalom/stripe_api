import pytest
from model_bakery import baker

from stripe_integration.actions.subscription_report_created import SubscriptionReportCreated
from stripe_integration.models import Subscription
from stripe_integration.tests.fakers import FakeStripeSubscription


@pytest.mark.django_db
class TestSubscriptionReportCreated:

    def test_subscription_report_updated(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        customer = baker.make('stripe_integration.Customer', payment_method=payment_method)
        subscription = baker.make('stripe_integration.Subscription', customer=customer, status=Subscription.UNPAID)

        stripe_subscription = FakeStripeSubscription(
            subscription.stripe_id,
            customer.stripe_id,
            Subscription.ACTIVE
        )

        result = SubscriptionReportCreated(stripe_subscription).process()
        assert result is True
        subscription.refresh_from_db()
        assert subscription.status == Subscription.ACTIVE

    def test_subscription_report_created_not_found(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        customer = baker.make('stripe_integration.Customer', payment_method=payment_method)
        subscription = baker.make('stripe_integration.Subscription', customer=customer, status=Subscription.UNPAID)

        stripe_subscription = FakeStripeSubscription(
            "subscription.stripe_id",
            "customer.stripe_id",
            Subscription.ACTIVE
        )

        result = SubscriptionReportCreated(stripe_subscription).process()
        assert result is False
        subscription.refresh_from_db()
        assert subscription.status == Subscription.UNPAID
