## Hint 1

A `path()` entry has two parts you care about: the pattern (`"items/<int:pk>/"`) and the view. Which part decides that `/items/abc/` is a 404? Which converter only matches digits, and which only matches letters, digits, `-` and `_`?

## Hint 2

The view receives the converted parts as **keyword arguments** with the same names as in the pattern, so `def item_detail(request, pk)` needs `<int:pk>` and `def article_detail(request, slug)` needs `<slug:slug>`. `JsonResponse` takes a dict. `slug.replace("-", " ").title()` builds the title.

## Hint 3

```text
home:           return HttpResponse("Welcome", content_type="text/plain")
item_detail:    return JsonResponse({"id": pk, "kind": "item"})
article_detail: return JsonResponse({"slug": slug, "title": slug.replace("-", " ").title()})
urlpatterns = [path("", home), path("items/<int:pk>/", item_detail), path("articles/<slug:slug>/", article_detail)]
```
