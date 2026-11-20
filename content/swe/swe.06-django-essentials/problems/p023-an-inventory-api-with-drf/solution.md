## Approach

```python
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
```

- The `ModelSerializer` builds fields from the model: `unique=True` on `sku` becomes a unique check (a duplicate is a clean 400), `DecimalField` becomes a string in JSON, a foreign key becomes the id.
- `read_only_fields = ["quantity"]` drops the sent value silently (the response is 200 or 201 with the real value). That is the design: the chapter's project changes stock only through audited movements.
- `validate_price` runs after the field's own checks and gives `400 {"price": [...]}`.
- `select_related("category")` makes the list one JOIN query instead of 1 + N.
- `IsAuthenticated` answers 403 for anonymous requests here, because the default first authentication class is `SessionAuthentication`, which has no way to challenge (Basic or token authentication would give 401).

## Complexity

A list is one query: O(items) rows read and serialised. A single item is one query for the row (plus one for a write).

## Another way

Add `DjangoModelPermissions` (as the chapter does) to reuse the admin's add/change/delete permissions instead of "any logged-in user". Add `PageNumberPagination` in `REST_FRAMEWORK` settings to wrap lists in `{"count", "next", "previous", "results"}`; the query count then becomes 2 (one for the count). For a read-only API use `ReadOnlyModelViewSet`.
