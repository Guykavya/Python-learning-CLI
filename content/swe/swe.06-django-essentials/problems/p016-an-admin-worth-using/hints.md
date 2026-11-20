## Hint 1

All these options are attributes of your `ItemAdmin` class. Which attribute controls the columns? Which one adds the search box and decides which columns it looks in? Which one lists fields as read-only text instead of form inputs?

## Hint 2

`list_display`, `search_fields`, `list_filter`, `readonly_fields` and `actions` are tuples or lists of names. An action is a method `def mark_discontinued(self, request, queryset)`; the name goes into `actions = ["mark_discontinued"]` and `@admin.action(description="...")` sets the label. Inside, `queryset.update(discontinued=True)` changes all selected rows in one statement. Permissions need no code: the admin checks `view_item`, `change_item` and so on for you.

## Hint 3

```text
list_display    = ("name", "sku", "category", "quantity", "discontinued")
search_fields   = ("name", "sku")
list_filter     = ("category", "discontinued")
readonly_fields = ("quantity",)
actions         = ["mark_discontinued"]

@admin.action(description="Mark selected items as discontinued")
def mark_discontinued(self, request, queryset):
    queryset.update(discontinued=True)
```
