from django.db import models

# Create your models here.


class StripeTrack(models.Model):
    created_at = models.DateTimeField(verbose_name="Creation date", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Last update", auto_now=True)
    stripe_id = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True


class PaymentMethod(StripeTrack):
    """
    Payment method information.
    We're assuming that this integration only manages credit/debit cards
    """
    LAST_DIGITS_LENGTH = 4

    last_digits = models.CharField(max_length=LAST_DIGITS_LENGTH,
                                   help_text="Only save 4 last characters because of security reasons")
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return f"PaymentMethod ID: {self.stripe_id}"


class Customer(StripeTrack):
    """
    Customer information
    """

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    invoice_prefix = models.CharField(max_length=100, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)

    def __str__(self):
        return f"Customer {self.full_name}"


class Subscription(StripeTrack):
    """
    Subscription information
    We're assiming that each a customer only can have a product/price in each subscription
    """

    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

    STATUS = (
        (INCOMPLETE, "Incomplete"),
        (INCOMPLETE_EXPIRED, "Incomplete expired"),
        (TRIALING, "Trialing"),
        (ACTIVE, "Active"),
        (PAST_DUE, "Past Due"),
        (CANCELED, "Canceled"),
        (UNPAID, "Unpaid"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    price_id = models.CharField(verbose_name="Stripe Price ID", max_length=100)
    status = models.CharField(max_length=20, choices=STATUS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Subscription {self.price_id} - {self.get_status_display()}"
