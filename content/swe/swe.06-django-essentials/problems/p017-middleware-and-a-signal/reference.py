import re
import uuid

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.urls import path


class Item(models.Model):
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    threshold = models.IntegerField(default=5)

    class Meta:
        app_label = "shop"


class LowStockAlert(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="alerts")
    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "shop"


VALID_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.headers.get("X-Request-ID", "")
        request.request_id = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


@receiver(pre_save, sender=Item)
def remember_old_quantity(sender, instance, **kwargs):
    old = Item.objects.filter(pk=instance.pk).values_list("quantity", flat=True).first() if instance.pk else None
    instance._was_low = old is not None and old < instance.threshold


@receiver(post_save, sender=Item)
def alert_on_crossing(sender, instance, created, **kwargs):
    is_low = instance.quantity < instance.threshold
    if is_low and not instance._was_low:
        LowStockAlert.objects.create(item=instance, quantity=instance.quantity)


def whoami(request):
    return JsonResponse({"request_id": request.request_id})


urlpatterns = [path("whoami/", whoami)]
