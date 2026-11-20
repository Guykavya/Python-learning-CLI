## Approach

```python
@require_http_methods(["GET", "POST"])
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("item_list")
    else:
        form = ItemForm()
    return render_form(request, form)


urlpatterns = [
    path("items/", item_list, name="item_list"),
    path("items/new/", item_create, name="item_create"),
]
```

- **One view, three outcomes.** GET builds an *unbound* form (no data). POST builds a *bound* form from `request.POST`. `is_valid()` runs all checks and fills `form.errors`. A bound invalid form renders itself with the typed values and an `errorlist` under each bad field, so the code after the `if` shows it again with status 200.
- **Redirect after a successful POST (POST/redirect/GET).** If you answered 200 with the page, the browser's refresh button would repeat the POST and create a duplicate. A 302 makes the browser do a fresh GET of the list page. `redirect("item_list")` reverses the URL name, so changing the path later does not break the view.
- **CSRF.** `CsrfViewMiddleware` hands the browser a secret cookie and puts a token (derived from it) into the form with `{% csrf_token %}`. On POST it compares the two. A foreign site can make your user's browser send a POST (the cookie goes along) but cannot read the token, so it fails with 403. The token reaches the template only if the template is rendered **with the request** (the `render_form` helper does this).
- `require_http_methods(["GET", "POST"])` answers 405 and an `Allow` header for any other method.
- A duplicate `sku` is found by `form.is_valid()` (`validate_unique`), so it is a normal form error, not a 500 page.

## Complexity

One `SELECT` for the uniqueness check and one `INSERT` on success.

## Another way

`CreateView` (section 12.1) does exactly this with `form_class`, `template_name` and `success_url`, in about five lines. Writing it by hand once shows what the generic view hides; you also need it when a form needs extra steps (setting `owner = request.user` before saving, with `form.save(commit=False)`).
