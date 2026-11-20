# Show, validate, redirect

Chapter section 11.3. Every form page follows the same three steps: **show** the empty form on GET; on POST **validate**, and if the data is bad show the form again with the errors (status 200); if it is good **save and redirect** (status 302) so a page refresh does not send the form twice.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run. The `CsrfViewMiddleware` is active, and the test client **enforces** it: a POST without a valid token gets 403, as in a real browser.

The starter already has the model `Item` (`name`, `sku` unique, `price`), a `ModelForm` called `ItemForm`, a list view `item_list` at `/items/` (name `item_list`) and a helper `render_form(request, form)` that renders the page with the form and a `{% csrf_token %}` (you do not write templates). Write the view `item_create(request)` at `/items/new/` (name `item_create`) and add it to `urlpatterns`:

- **GET**: status 200, the page contains the empty form.
- **POST with invalid data**: status 200, the page is shown again with the form's errors (`errorlist`) and with the values the user typed; **no** item is saved.
- **POST with valid data**: save one `Item`, then answer **302** with `Location: /items/`. Build the target with `redirect("item_list")`, not by writing the URL.
- Other methods (for example `DELETE`) are answered with **405** (use `require_http_methods`).

## Example

```text
GET  /items/new/                                  -> 200 (form with name, sku, price)
POST /items/new/  name=Pen sku=AB-1 price=abc     -> 200 (errors shown, nothing saved)
POST /items/new/  name=Pen sku=AB-1 price=1.50    -> 302 Location: /items/ (one new Item)
POST without the csrf token                       -> 403 (done by the middleware, not by you)
```
