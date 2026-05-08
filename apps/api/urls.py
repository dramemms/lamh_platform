from django.urls import path
from .views import kobo_accident_webhook

urlpatterns = [
    path("kobo/accident-webhook/", kobo_accident_webhook, name="kobo_accident_webhook"),
]