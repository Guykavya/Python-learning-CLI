## Hint 1

Start from the failing test message. Three separate things are needed: the serializer (what the JSON looks like and which input is accepted), the viewset (who may call it and which queryset it uses), and the URLs (the router). Which of the three fails first for a test that only calls `GET /api/items/` as an anonymous user?

## Hint 2

In a `ModelSerializer`, `Meta.fields` lists the fields, `read_only_fields` makes `quantity` ignored on input, and a method named `validate_<field>(self, value)` checks one field and raises `serializers.ValidationError`. `category_name = serializers.CharField(source="category.name", read_only=True)` reads through the relation, so the viewset's queryset needs `select_related("category")`, or every row costs one more query. `permission_classes = [IsAuthenticated]` goes on the viewset.

## Hint 3

```text
class ItemSerializer(ModelSerializer):
    category_name = CharField(source="category.name", read_only=True)
    Meta: model = Item; fields = [id, name, sku, quantity, price, category, category_name]; read_only_fields = ["quantity"]
    validate_price(value): if value <= 0: raise ValidationError; return value
class ItemViewSet(ModelViewSet): queryset = Item.objects.select_related("category"); serializer_class; permission_classes = [IsAuthenticated]
router = DefaultRouter(); router.register("items", ItemViewSet); urlpatterns = [path("api/", include(router.urls))]
```
