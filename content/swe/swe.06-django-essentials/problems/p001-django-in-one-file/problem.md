# Django in one file

Chapter sections 1.4, 4.1 and 4.2. A Django site is a list of `path()` entries and functions that take a request and return a response. Here you write a very small one.

In `solution.py` write three **function views** and a list called `urlpatterns`. (The tests set Django up for you and use your `urlpatterns` as the site's URLconf, as the chapter's section 1.4 does with `ROOT_URLCONF`.)

| URL | View | Answer |
|---|---|---|
| `/` | `home(request)` | plain text `Welcome` (`Content-Type` starts with `text/plain`) |
| `/items/<int:pk>/` | `item_detail(request, pk)` | JSON `{"id": pk, "kind": "item"}`, with `pk` an **int** |
| `/articles/<slug:slug>/` | `article_detail(request, slug)` | JSON `{"slug": slug, "title": ...}` where the title is the slug with `-` replaced by spaces and every word capitalised |

URLs that match no entry (`/items/abc/`, `/items/-1/`, `/articles/has space/`, `/nope/`) must give a **404**. You do not write any code for that: it follows from the converters.

The starter already has the three function names and an empty `urlpatterns`. Use `HttpResponse` (with `content_type=`) for the plain text and `JsonResponse` for the JSON.

## Example

```text
GET /                          -> 200  Welcome
GET /items/42/                 -> 200  {"id": 42, "kind": "item"}
GET /items/abc/                -> 404  (no entry matches)
GET /articles/learn-django/    -> 200  {"slug": "learn-django", "title": "Learn Django"}
```
