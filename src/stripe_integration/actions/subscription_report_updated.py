import logging
import stripe

from django.conf import settings

from django.db import transaction

from stripe_integration.actions.utils import price_amount
from stripe_integration.models import Subscription


logger = logging.getLogger(__name__)


class SubscriptionReportUpdated:

    """
    Class to register the information that stripe send to the webhook when a Subscription has been updated.

    On the process method of this class, first we check that the subscription exists on the DB by stripe ID and
    customer stripe ID.

    If the we don't find the subscription on the DB, we return a False to indicate that the hasn't
    finished properly.

    If we find the subscription, if stripe subscription status or plan amount has changed, we update the subscription
    on the DB and return a True to indicate that the process has finished properly.
    """

    stripe.api_key = settings.STRIPE_API_KEY

    subscription = None

    def __init__(self, subscription) -> None:
        super().__init__()
        self.subscription = subscription

    def process(self):
        with transaction.atomic():
            try:
                db_subscription = Subscription.objects.get(
                    stripe_id=self.subscription.id,
                    customer__stripe_id=self.subscription.customer
                )
            except Subscription.DoesNotExist:
                logger.error(
                    f"Subscription with id {self.subscription.id} for customer {self.subscription.customer} not found"
                )
                return False

        if self.subscription.status != db_subscription.status:
            db_subscription.status = self.subscription.status
            logger.info(f"Subscription {self.subscription.id} updated to {self.subscription.status}")

        subscription_amount = price_amount(self.subscription.plan.amount)
        if subscription_amount != db_subscription.amount:
            db_subscription.amount = subscription_amount
            logger.info(f"Subscription {self.subscription.id} updated to {subscription_amount}")

        db_subscription.save()
        return True
