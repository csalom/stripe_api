import logging
import stripe

from django.conf import settings
from django.db import transaction

from stripe_integration.models import Subscription


logger = logging.getLogger(__name__)


class SubscriptionReportCreated:
    """
    Class to register the information that stripe send to the webhook when a Subscription has been created.

    On the process method of this class, first we check that the subscription exists on the DB by stripe ID and
    customer stripe ID.

    If the we don't find the subscription on the DB, we return a False to indicate that the hasn't
    finished properly.

    If we find the subscription, we updated the status to the one that stripe has sent and return a True to indicate
    that it has finished correctly.
    """

    stripe.api_key = settings.STRIPE_API_KEY

    subscription = None

    def __init__(self, subscription) -> None:
        super().__init__()
        self.subscription = subscription

    def process(self) -> bool:
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

        db_subscription.status = self.subscription.status
        db_subscription.save()

        if self.subscription.status == Subscription.ACTIVE:
            logger.info(f"Subscription {self.subscription.id} set to active")
        else:
            logger.info(f"Subscription {self.subscription.id} set to {self.subscription.status}")
        return True
