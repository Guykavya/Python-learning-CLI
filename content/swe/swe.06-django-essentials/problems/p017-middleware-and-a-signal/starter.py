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


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # TODO: choose the id, set request.request_id, add the response header
        return self.get_response(request)


# TODO: receivers for pre_save and post_save of Item


def whoami(request):
    return JsonResponse({"request_id": request.request_id})


urlpatterns = [path("whoami/", whoami)]
