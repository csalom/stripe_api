from decimal import Decimal


def price_amount(unit_amount):
    return Decimal(unit_amount / 100)
