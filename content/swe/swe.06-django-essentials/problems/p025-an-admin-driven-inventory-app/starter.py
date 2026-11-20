from django.conf import settings
from django.contrib import admin
from django.db import IntegrityError, models, transaction
from django.db.models import F
from django.urls import include, path
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter


# --- models ---------------------------------------------------------------------------------------
# TODO: give every model its real fields (see problem.md), __str__, and a CheckConstraint on Item.

class Category(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        app_label = "shop"


class Item(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "shop"


class Movement(models.Model):
    class Reason(models.TextChoices):
        RECEIVE = "receive", "Goods received"
        SALE = "sale", "Sale"
        ADJUST = "adjust", "Stock-take adjustment"

    note = models.CharField(max_length=200, blank=True)

    class Meta:
        app_label = "shop"


# --- the one function that changes stock ----------------------------------------------------------

class InsufficientStock(Exception):
    pass


def move_stock(item, delta, reason, user=None, note=""):
    raise NotImplementedError("TODO: atomic, F(), refuse to go below zero, one Movement row")


# --- admin ----------------------------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass                                   # TODO: list_display, list_filter, search_fields, readonly_fields


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    pass                                   # TODO: an audit trail: nobody adds, changes or deletes rows


# --- API ------------------------------------------------------------------------------------------

class ItemSerializer(serializers.Serializer):          # TODO: a read-only ModelSerializer of Item
    pass


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()                      # TODO: no N+1; logged-in users only; the "move" action for staff
    serializer_class = ItemSerializer


router = DefaultRouter()                               # TODO: register the viewset under "items"

urlpatterns = [
    path("admin/", admin.site.urls),
    # TODO: path("api/", include(router.urls)),
]
