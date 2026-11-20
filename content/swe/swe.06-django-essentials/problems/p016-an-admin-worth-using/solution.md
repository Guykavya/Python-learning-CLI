## Approach

```python
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "quantity", "discontinued")
    search_fields = ("name", "sku")
    list_filter = ("category", "discontinued")
    readonly_fields = ("quantity",)
    actions = ["mark_discontinued"]

    @admin.action(description="Mark selected items as discontinued")
    def mark_discontinued(self, request, queryset):
        updated = queryset.update(discontinued=True)
        self.message_user(request, f"{updated} item(s) marked as discontinued.")
```

- **`list_display`** chooses the columns of the list page. A foreign key column shows `str(category)`; add `list_select_related = ("category",)` on bigger lists so the admin does not run one query per row.
- **`search_fields`** adds the search box; the admin builds `name ICONTAINS q OR sku ICONTAINS q` for each word. The query parameter is `q`.
- **`list_filter`** adds the right-hand panel; the filter for a foreign key uses `?category__id__exact=<id>`, for a boolean `?discontinued__exact=1`.
- **`readonly_fields`** removes the field from the form class. Because it is not a form field, a POST value for it is ignored, which is the real protection: hiding an input is not enough, the server must not read it. A stock number that changes only through recorded movements stays honest.
- **An action** receives the selected rows as a queryset. `update()` does it in one SQL statement; it does not call `save()` and sends no signals.
- **Permissions are free.** The admin checks the model permissions `view_`, `add_`, `change_`, `delete_` on every view. Staff with only `view_item` can open the page (it is shown without inputs), but the POST fails with 403. A user with no permission gets 403, an anonymous visitor is redirected to the login page.

## Complexity

The changelist runs one query for the rows, one for the count (plus one per filter and one per foreign-key row, unless `list_select_related` is set). The action is one `UPDATE`.

## Another way

You can exclude the field with `exclude = ("quantity",)`, but then the page does not show it at all. A custom column `def stock(self, obj): ...` listed in `list_display` can format the number (for example a red "LOW" label) while the real field stays read-only. For stricter rules override `has_change_permission(self, request, obj=None)`.
