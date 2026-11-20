# An admin worth using

Chapter sections 10.1 to 10.3. The admin gives you a back office for free, but the free version shows only `__str__`, cannot search and lets everybody with change permission edit the stock number directly. Make it useful and safe.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run. The admin URLs are `/admin/...`: the starter's `urlpatterns` already include `path("admin/", admin.site.urls)`, keep it. (The tests make the admin permissions themselves; you do not need migrations.)

The starter has `Category` (`name`) and `Item` (`name`, `sku`, `quantity`, `discontinued`, `category`) and registers a plain `ItemAdmin`. Improve `ItemAdmin`:

1. `list_display` shows `name`, `sku`, `category`, `quantity` and `discontinued` (all five, in this order).
2. `search_fields` lets the search box (`?q=...`) find an item by `name` or by `sku`.
3. `list_filter` offers a filter on `category` and on `discontinued`.
4. `quantity` is **read-only** (`readonly_fields`): it is shown on the change page but a POST that contains `quantity` must not change it (stock changes only through movements; you build that in the project).
5. An admin **action** named `mark_discontinued` ("Mark selected items as discontinued") sets `discontinued=True` on the selected rows with one `update()` call.
6. Permissions come from Django, you write no code for them: a staff user who only has the `view_item` permission may open the change page (200) but a POST there is refused with **403**; a staff user with no permission at all gets 403 on the changelist; an anonymous visitor is redirected (302) to the login page.

## Example

```text
superuser GET /admin/shop/item/?q=PEN       -> 200, only items whose name or sku contains "pen" (any case)
superuser POST action mark_discontinued     -> 302, the selected items now have discontinued=True
view-only staff POST /admin/shop/item/1/change/ -> 403
```
