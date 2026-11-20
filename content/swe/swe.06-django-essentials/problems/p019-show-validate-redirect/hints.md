## Hint 1

Write the three cases on paper: GET, POST with bad data, POST with good data. Which two cases return a page and which returns a redirect? In the bad case, which form must you show: a new empty one, or the one that already holds the POST data and its errors?

## Hint 2

```text
if request.method == "POST":
    form = ItemForm(request.POST)         # bound form: keeps the data and the errors
    if form.is_valid():
        form.save()
        return redirect("item_list")      # name of the URL, not the path
else:
    form = ItemForm()                     # unbound form for GET
return render_form(request, form)         # reached for GET and for an invalid POST
```

The CSRF check is not your job: the middleware stops a POST without a valid token before your view runs. Add `@require_http_methods(["GET", "POST"])` for the 405, and the `path("items/new/", item_create, name="item_create")` entry.

## Hint 3

Everything in the schema above is the whole function. The one common slip is to build `ItemForm()` again after a failed POST: the user then loses what they typed and sees no errors.
