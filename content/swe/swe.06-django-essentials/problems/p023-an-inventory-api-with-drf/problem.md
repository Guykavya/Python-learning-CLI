# An inventory API with DRF

Chapter sections 15.2 to 15.4 and "Try it: why is `quantity` ignored?". Build a small JSON API for items with Django REST Framework.

`solution.py` already has the models `Category` (a `name`) and `Item` (`name`, unique `sku`, `quantity`, `price`, `category`). You write, in the same file:

1. `ItemSerializer`, a `ModelSerializer` for `Item` with the fields `id`, `name`, `sku`, `quantity`, `price`, `category` and `category_name`.
   - `category` is the category's id; `category_name` is read-only and comes from `source="category.name"`.
   - `quantity` is **read-only**: stock changes through movements (later), never through the API fields. Sent values are ignored, not an error.
   - `validate_price(value)`: a price of 0 or less is rejected, so the response is `400` with the error under the key `price`.
2. `ItemViewSet`, a `ModelViewSet` using `ItemSerializer`. Only **logged-in** users may use it (`IsAuthenticated`; set it on the view, the tests do not set DRF settings). Listing items must not run one query per item.
3. `router = DefaultRouter()` with the viewset registered under `"items"`, and `urlpatterns = [path("api/", include(router.urls))]`, so the URLs are `/api/items/` and `/api/items/<pk>/`.

No pagination is configured, so `GET /api/items/` returns a plain JSON list.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`; do not change a model while tests run. The models are given: leave them as they are.

## Example

```text
anonymous GET  /api/items/                          -> 403
POST /api/items/ {"name": "Gadget", "sku": "GD-1", "price": "9.99", "category": 1, "quantity": 999}
                                                     -> 201 {"id": 1, "name": "Gadget", "sku": "GD-1", "quantity": 0,
                                                             "price": "9.99", "category": 1, "category_name": "Cables"}
POST ... "price": "-1"                               -> 400 {"price": ["..."]}
GET  /api/items/  with 12 items                      -> 200, one SQL query
```
