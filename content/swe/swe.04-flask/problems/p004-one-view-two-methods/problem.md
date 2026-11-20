# One view, two methods

Chapter section 3.4. The same URL often has two jobs: **GET** shows a form, **POST** handles it. In `solution.py` write `create_app()` with one route `/contact` (one view function, `methods=["GET", "POST"]`):

- `GET /contact` answers **200** with HTML that contains `<form method="post"` and an input named `name`.
- `POST /contact` with form field `name=Asha` answers **200** with `Thanks, Asha!`. The name is HTML-escaped in the answer (a name like `<b>` must not appear as a tag). If `name` is missing or blank, answer **400** with `Name is required`.
- Any other method (for example `PUT`) is rejected by Flask with **405**, and the `Allow` header lists exactly `GET, HEAD, OPTIONS, POST`. You get that for free if you declare the methods correctly; do not write code for it.

Use `request.method` to decide inside the view and `request.form` for the data.

## Example

```text
GET  /contact                       -> 200 (the form)
POST /contact   name=Asha           -> 200 Thanks, Asha!
POST /contact   name=               -> 400 Name is required
PUT  /contact                       -> 405  Allow: GET, HEAD, OPTIONS, POST
```
