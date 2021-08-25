import stripe
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from django.conf import settings

from stripe_integration.actions.subscription_report_created import SubscriptionReportCreated
from stripe_integration.actions.subscription_report_updated import SubscriptionReportUpdated
from stripe_integration.serializers import SubscriptionCreateSerializer, SubscriptionCreatedSerializer


class CreateSubscriptionView(CreateAPIView):
    """
    View to validate and register data for subscription creation.
    Inside the serializer, the subscription is created in Stripe too.
    """
    serializer_class = SubscriptionCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.validated_data)
        return Response(
            SubscriptionCreatedSerializer(self._retrieve_instance(serializer)).data,
            status=HTTP_201_CREATED,
            headers=headers
        )

    @staticmethod
    def _retrieve_instance(serializer):
        return getattr(serializer, "instance", None)


class StripeWebHookView(APIView):
    """
    Webhook endpoint that needs to be opened to internet, so no authentication nor permission classes are setted.
    Due to this fact, we use the HTTP_STRIPE_SIGNATURE header to validate that the request has been done by stripe.
    This is the way that stripe suggest to prevent any attack.

    If the request is not valid, we're going to return an http 400.
    If the request is valid, after constructing the event, we are going to call the logic class to handle it.
    If we find the subscription related on the DB, we're going to update the data and return a http 200 else we're going
    to return a http 404.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            event = self._retrieve_stripe_event(request.body, request.META.get("HTTP_STRIPE_SIGNATURE", ''))
        except (ValueError, stripe.error.SignatureVerificationError):
            # Invalid payload
            return Response(status=HTTP_400_BAD_REQUEST)

        if event.type == "customer.subscription.created":
            sucessfull = SubscriptionReportCreated(event.data.object).process()
            if not sucessfull:
                return Response(status=HTTP_404_NOT_FOUND)

        elif event.type == "customer.subscription.updated":
            sucessfull = SubscriptionReportUpdated(event.data.object).process()
            if not sucessfull:
                return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_200_OK)

    @staticmethod
    def _retrieve_stripe_event(body, stripe_signature):
        # Construct event with stripe signature and webhook secret to confirm that the request was send by stripe
        return stripe.Webhook.construct_event(
            body, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
