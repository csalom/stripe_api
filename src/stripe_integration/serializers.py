from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import Serializer, IntegerField, CharField, EmailField, ModelSerializer

from stripe_integration.actions.subscription_create import SubscriptionCreate
from stripe_integration.models import Subscription, Customer, PaymentMethod


class SubscriptionCreateSerializer(Serializer):

    """
    Serializer to validate subscriptioon creation data
    """

    full_name = CharField(max_length=100)
    email = EmailField()
    card_number = CharField(max_length=16)
    month = IntegerField(max_value=12, min_value=1)
    year = IntegerField()
    cvc = IntegerField()
    price_id = CharField(max_length=100)

    def run_validation(self, data=empty):
        validated_data = super().run_validation(data)
        current_year = timezone.now().year
        current_month = timezone.now().month
        validation_errors = {}

        if self._email_exists(validated_data["email"]):
            validation_errors.update({"email": "Customer email alredy exists. You must use another one"})

        if not validated_data["card_number"].isdigit():
            validation_errors.update({"last_digits": "Last digits value must be a digit"})

        if validated_data["year"] < current_year:
            validation_errors.update({"year": "Year must be the current or a future one"})

        if validated_data["month"] < current_month and validated_data["year"] == current_year:
            validation_errors.update({"month": "Month must be the current or a future one"})

        if validation_errors:
            raise ValidationError(validation_errors)

        return validated_data

    @staticmethod
    def _email_exists(email):
        return Customer.objects.filter(email=email).exists()

    def create(self, validated_data):
        return SubscriptionCreate(**validated_data).process()


class PaymentMethodSerializer(ModelSerializer):

    class Meta:
        model = PaymentMethod
        fields = ("id", "created_at", "stripe_id", "last_digits", "month", "year")
        read_only_fields = fields


class CustomerSerializer(ModelSerializer):

    payment_method = PaymentMethodSerializer()

    class Meta:
        model = Customer
        fields = ("id", "created_at", "stripe_id", "full_name", "email", "invoice_prefix", "payment_method")
        read_only_fields = fields


class SubscriptionCreatedSerializer(ModelSerializer):

    customer = CustomerSerializer()

    class Meta:
        model = Subscription
        fields = ("id", "created_at", "stripe_id", "price_id", "status", "amount", "customer")
        read_only_fields = fields
