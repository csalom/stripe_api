from django.urls import path

from . import views

urlpatterns = [
    path('subscription/', views.CreateSubscriptionView().as_view(), name='subscription-create'),
    path('webhook/', views.StripeWebHookView().as_view(), name='subscription-webhook'),
]
