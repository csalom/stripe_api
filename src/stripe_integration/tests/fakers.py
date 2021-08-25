from stripe_integration.models import Subscription


class FakerStripePrice:

    id = "price_w42sdf45t"
    unit_amount = 10000

    def __init__(self, price_id=None, unit_amount=None) -> None:
        super().__init__()
        if price_id:
            self.id = price_id
        if unit_amount:
            self.unit_amount = unit_amount


class FakerStripePaymentMethod:
    id = "pam_asd2345asda"

    def __init__(self, payment_method_id=None) -> None:
        super().__init__()
        if payment_method_id:
            self.id = payment_method_id

    def attach(self, customer):
        pass


class FakerStripeCustomer:
    id = "cus_asd2345a23"
    invoice_prefix = "INVOX"

    def __init__(self, customer_id=None, invoice_prefix=None) -> None:
        super().__init__()
        if customer_id:
            self.id = customer_id
        if invoice_prefix:
            self.invoice_prefix = invoice_prefix


class FakerStripePlan:
    amount = 10000

    def __init__(self, amount=None) -> None:
        super().__init__()
        if amount:
            self.amount = amount


class FakeStripeSubscription:
    id = None
    customer = None
    status = None

    def __init__(self, sub_id, customer, status, amount=None) -> None:
        super().__init__()
        self.id = sub_id
        self.customer = customer
        self.status = status
        self.plan = FakerStripePlan(amount=amount)


class FakeStripeData:
    object = None

    def __init__(self) -> None:
        super().__init__()
        self.object = FakeStripeSubscription("1", "cus_asda34r5asdf", Subscription.ACTIVE)


class FakeStripeEvent:
    type = None
    data = None

    def __init__(self, event_type) -> None:
        super().__init__()
        self.type = event_type
        self.data = FakeStripeData()
