from rest_framework import serializers

from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low = serializers.BooleanField(read_only=True)
    sku = serializers.CharField(max_length=20, validators=[])      # uniqueness is checked by hand below

    class Meta:
        model = Product
        fields = ["id", "name", "sku", "category", "category_name", "price", "quantity", "reorder_level", "is_low"]
        read_only_fields = ["quantity"]            # quantity changes only through stock movements

    def validate_sku(self, value):
        value = value.strip().upper()
        others = Product.objects.filter(sku=value)
        if self.instance is not None:
            others = others.exclude(pk=self.instance.pk)
        if others.exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be above zero.")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ["id", "product", "delta", "reason", "note", "created"]
        read_only_fields = ["id", "product", "created"]

    def validate_delta(self, value):
        if value == 0:
            raise serializers.ValidationError("Delta must not be zero.")
        return value
