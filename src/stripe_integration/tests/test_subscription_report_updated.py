from decimal import Decimal

import pytest
from model_bakery import baker

from stripe_integration.actions.subscription_report_updated import SubscriptionReportUpdated
from stripe_integration.models import Subscription
from stripe_integration.tests.fakers import FakeStripeSubscription


@pytest.mark.django_db
class TestSubscriptionReportUpdated:

    def test_subscription_report_updated(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        customer = baker.make('stripe_integration.Customer', payment_method=payment_method)
        subscription = baker.make(
            'stripe_integration.Subscription',
            customer=customer,
            status=Subscription.UNPAID,
            amount=Decimal(100)
        )

        stripe_subscription = FakeStripeSubscription(
            subscription.stripe_id,
            customer.stripe_id,
            Subscription.ACTIVE,
            amount=20000
        )

        result = SubscriptionReportUpdated(stripe_subscription).process()
        assert result is True
        subscription.refresh_from_db()
        assert subscription.status == Subscription.ACTIVE
        assert subscription.amount == Decimal(200)

    def test_subscription_report_updated_not_found(self):
        payment_method = baker.make('stripe_integration.PaymentMethod')
        customer = baker.make('stripe_integration.Customer', payment_method=payment_method)
        subscription = baker.make(
            'stripe_integration.Subscription',
            customer=customer,
            status=Subscription.UNPAID,
            amount=Decimal(100)
        )

        stripe_subscription = FakeStripeSubscription(
            "subscription.stripe_id",
            "customer.stripe_id",
            Subscription.ACTIVE,
            amount=20000
        )

        result = SubscriptionReportUpdated(stripe_subscription).process()
        assert result is False
        subscription.refresh_from_db()
        assert subscription.status == Subscription.UNPAID
        assert subscription.amount == Decimal(100)
