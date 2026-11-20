from django.db import models
from django.urls import include, path
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter


class Category(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        app_label = "shop"


class Item(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=20, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    class Meta:
        app_label = "shop"


class ItemSerializer(serializers.Serializer):          # TODO: a ModelSerializer for Item
    pass


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()                    # TODO: avoid one query per item for the category
    serializer_class = ItemSerializer                # TODO: only logged-in users may use it


router = DefaultRouter()                             # TODO: register the viewset under "items"
urlpatterns = []                                     # TODO: path("api/", include(router.urls))
