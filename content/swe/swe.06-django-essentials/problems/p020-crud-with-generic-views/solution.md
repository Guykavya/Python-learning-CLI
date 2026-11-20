## Approach

```python
class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    ordering = ["name"]


class ItemDetailView(DetailView):
    model = Item
    template_name = "items/detail.html"


class ItemCreateView(CreateView):
    model = Item
    fields = ["name", "quantity"]
    template_name = "items/form.html"
    success_url = reverse_lazy("item_list")


class ItemUpdateView(UpdateView):
    model = Item
    fields = ["name", "quantity"]
    template_name = "items/form.html"
    success_url = reverse_lazy("item_list")
```

- **Each generic view is the three-step form view in disguise.** `CreateView` builds a `ModelForm` from `model` and `fields`, shows it on GET, validates on POST, saves and redirects to `success_url`; on invalid data it renders the template again with status 200. `UpdateView` does the same with an instance loaded from the URL.
- **`fields` is an allow-list** (see the mass-assignment section): only `name` and `quantity` are editable. `fields = "__all__"` would expose every column.
- **The 404 is free.** `DetailView` and `UpdateView` call `get_object_or_404` with the `pk` from the URL (`<int:pk>`), so an unknown pk gives a 404 without any code.
- **`template_name`.** If you leave it out, Django looks for `shop/item_list.html`, `shop/item_detail.html`, `shop/item_form.html` (app label, model name, suffix). Here the tests provide `items/...` templates from memory, so you name them.
- **`reverse_lazy`** returns a lazy string, evaluated when the redirect happens. `reverse("item_list")` at class-definition time raises `NoReverseMatch` (the URLconf imports this module, and is not ready yet).
- The list template reads `object_list` (`context_object_name` would add `item_list` as another name).

## Complexity

List: one query. Detail and update: one `SELECT` by primary key. Create: one `INSERT`. Update: one `SELECT` and one `UPDATE`.

## Another way

Without generic views, each page is a function of 8 to 12 lines (see the previous problem). Generic views win when the page is plain CRUD; when you need a different flow, override one hook such as `get_queryset()` (limit the rows to the current user), `form_valid(form)` (set `form.instance.owner = request.user`) or `get_success_url()`, instead of rewriting the whole view.
