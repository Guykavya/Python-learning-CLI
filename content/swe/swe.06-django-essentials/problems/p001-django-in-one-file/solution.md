## Approach

```python
from django.http import HttpResponse, JsonResponse
from django.urls import path


def home(request):
    return HttpResponse("Welcome", content_type="text/plain")


def item_detail(request, pk):
    return JsonResponse({"id": pk, "kind": "item"})


def article_detail(request, slug):
    return JsonResponse({"slug": slug, "title": slug.replace("-", " ").title()})


urlpatterns = [
    path("", home),
    path("items/<int:pk>/", item_detail),
    path("articles/<slug:slug>/", article_detail),
]
```

- Django goes through `urlpatterns` from the top and uses the first pattern that matches. A converter does two jobs: it decides **whether** a URL matches (`<int:...>` accepts digits only, so `/items/abc/` and `/items/-1/` match nothing) and it **converts** the text (the view gets `pk=42` as an int, not `"42"`).
- If no entry matches, Django itself answers 404. Your views never see these URLs, so you do not write a single `if`.
- `/items/7` (no final slash) is not a 404: `CommonMiddleware` has `APPEND_SLASH = True` by default and answers `301` with `Location: /items/7/`. This happens only for a **GET** and only when the URL with the slash would match.
- `JsonResponse` sets `Content-Type: application/json`; `HttpResponse` defaults to `text/html`, which is why `home` passes `content_type="text/plain"`.

## Complexity

Matching is a walk through the list of patterns: O(number of patterns). Each view is O(1).

## Another way

`path("items/<pk>/", ...)` (no converter) gives `pk` as a **string** and accepts `/items/abc/`; you would have to validate it yourself and raise `Http404`. Converters move that check into the URL, where it belongs. For a pattern a converter cannot express, `re_path()` takes a regular expression.
