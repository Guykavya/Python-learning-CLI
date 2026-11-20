## Hint 1

A generic view needs to know three things: which model, which template, and (for create and update) which fields and where to go after saving. Which attribute names do these? Why can the success URL not be computed with `reverse()` while Python loads the class body?

## Hint 2

`ListView` and `DetailView`: `model`, `template_name`; `ordering = ["name"]` sorts the list. `CreateView` and `UpdateView` also need `fields = ["name", "quantity"]` and `success_url = reverse_lazy("item_list")`. `reverse_lazy` waits until the URL is needed; `reverse` would run when the file is imported, before `urlpatterns` exists. The 404 for an unknown pk is already built in.

## Hint 3

```text
ItemListView:    model = Item;  template_name = "items/list.html";   ordering = ["name"]
ItemDetailView:  model = Item;  template_name = "items/detail.html"
ItemCreateView:  model = Item;  fields = [...]; template_name = "items/form.html"; success_url = reverse_lazy("item_list")
ItemUpdateView:  the same as ItemCreateView
```
