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


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "sku", "quantity", "price", "category", "category_name"]
        read_only_fields = ["quantity"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be above zero.")
        return value


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.select_related("category").order_by("id")
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]


router = DefaultRouter()
router.register("items", ItemViewSet)
urlpatterns = [path("api/", include(router.urls))]
