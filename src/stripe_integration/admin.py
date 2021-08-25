from django.contrib import admin

# Register your models here.

from stripe_integration.models import PaymentMethod, Customer, Subscription


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at", "stripe_id", "last_digits")
    list_filter = ("stripe_id", "last_digits")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at", "stripe_id", "email", "full_name")
    list_filter = ("stripe_id", "full_name", "email")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at", "stripe_id", "price_id", "status", "amount")
    list_filter = ("stripe_id", "price_id", "status", "amount")
    readonly_fields = ("id", "created_at", "updated_at")
