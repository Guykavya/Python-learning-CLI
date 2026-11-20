# Where does `reverse` point?

Chapter section 4.3. `reverse()` builds a URL from a **name**; it never makes a request. Below is a project URLconf with two `include()` calls, one app namespace (`app_name`) and one extra instance namespace. Six calls to `reverse` follow.

For each call write the URL that `reverse` returns, or the word `NoReverseMatch` if Django raises that error. (Reading the URLconf carefully is the whole task: which names exist, under which namespace, and which converter accepts which value.)

```python
import django
from django.conf import settings

settings.configure(ROOT_URLCONF=__name__)
django.setup()

from django.http import HttpResponse
from django.urls import NoReverseMatch, include, path, reverse


def view(request, *args, **kwargs):
    return HttpResponse("ok")


blog_patterns = [
    path("", view, name="index"),
    path("<slug:slug>/", view, name="post"),
    path("archive/<int:year>/", view, name="archive"),
]
shop_patterns = ([
    path("", view, name="index"),
    path("item/<int:pk>/", view, name="item"),
], "shop")

urlpatterns = [
    path("", view, name="home"),
    path("blog/", include((blog_patterns, "blog"))),
    path("store/", include(shop_patterns)),
    path("outlet/", include(shop_patterns, namespace="outlet")),
]

calls = [
    ("blog:post", {"kwargs": {"slug": "hello"}}),
    ("blog:archive", {"args": [2024]}),
    ("shop:item", {"kwargs": {"pk": 7}}),
    ("outlet:index", {}),
    ("post", {"kwargs": {"slug": "hello"}}),
    ("shop:item", {"kwargs": {"pk": "abc"}}),
]
for number, (name, options) in enumerate(calls, 1):
    try:
        result = reverse(name, **options)
    except NoReverseMatch:
        result = "NoReverseMatch"
    print(f"{number}: {result}")
```

Write your answer in `answer.txt`: six lines, `1: ...` to `6: ...`, in the format of the `print` above (for example `1: /blog/hello/`). Do not run it.

## After you answer

1. `blog_patterns` has a name `post`, yet call 5 fails. What is missing from the call, and why does the name alone not work?
2. The same list `shop_patterns` is included twice. How does Django know that `shop:item` means `/store/...` and not `/outlet/...`?
3. Why does call 6 fail even though `item` takes a `pk`? What would be the effect on a template that has `{% url 'shop:item' pk=user_text %}`?
