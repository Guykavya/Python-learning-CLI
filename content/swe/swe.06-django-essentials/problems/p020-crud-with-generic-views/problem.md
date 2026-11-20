# CRUD with generic views

Chapter section 12.1 and "Try it: where is the 404?". Four class-based generic views give you list, detail, create and update pages with a few attributes each.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run. **Extra setting for this problem:** there are no template files; the tests give Django three templates from memory (a `locmem` loader), so set `template_name` on each view to one of these names:

| `template_name` | Used by | What the template shows |
|---|---|---|
| `"items/list.html"` | `ItemListView` | `{% for item in object_list %}` name and quantity of each item |
| `"items/detail.html"` | `ItemDetailView` | `{{ object.name }}` and `{{ object.quantity }}` |
| `"items/form.html"` | `ItemCreateView`, `ItemUpdateView` | a `<form method="post">` with `{{ form.as_p }}` |

The starter has `Item` (`name`, `quantity`) and four empty view classes. Fill them in so these URLs work (the `urlpatterns` and their names are already in the starter):

| URL | Name | View | Behaviour |
|---|---|---|---|
| `/items/` | `item_list` | `ItemListView` | all items, ordered by `name` |
| `/items/<pk>/` | `item_detail` | `ItemDetailView` | one item; an unknown pk is a **404** |
| `/items/new/` | `item_create` | `ItemCreateView` | form with `name` and `quantity`; a valid POST saves and redirects (302) to `/items/` |
| `/items/<pk>/edit/` | `item_update` | `ItemUpdateView` | the same form filled with the item; a valid POST saves and redirects to `/items/`; unknown pk is a **404** |

Use `success_url = reverse_lazy("item_list")` (not `reverse`, which would run when the file is imported, before the URLconf exists). An invalid POST re-shows the form with status 200 and saves nothing.

## Example

```text
GET  /items/                      -> 200 (names in order)
GET  /items/999/                  -> 404
POST /items/new/  name=Pen quantity=3   -> 302 Location: /items/
POST /items/new/  name= quantity=3      -> 200 (form again), nothing saved
```
