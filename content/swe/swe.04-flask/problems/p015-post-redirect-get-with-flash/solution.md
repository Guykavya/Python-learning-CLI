## Approach

```python
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        values = {key: request.form.get(key, "").strip() for key in ("name", "message")}
        errors = {}
        if not values["name"]:
            errors["name"] = "Name is required"
        if len(values["message"]) < 10:
            errors["message"] = "Message must have at least 10 characters"
        if errors:
            return render_template_string(FORM, values=values, errors=errors)
        app.extensions["feedback"].append(values)
        flash(f"Thanks, {values['name']}!")
        return redirect(url_for("thanks"))
    return render_template_string(FORM, values={}, errors={})
```

Example: after the valid POST the browser's history ends with `GET /thanks`. Pressing F5 repeats that GET, which changes nothing. The message travels from the POST request to the GET request inside the **session cookie**: `flash()` puts it in, `get_flashed_messages()` takes it out.

For an **invalid** form there is no redirect: the user is still correcting the same form, and the typed values come back through the template.

## Complexity

`O(size of the form)`.

## Another way

Without `flash`, redirect to `/thanks?name=Asha`. It works, but the name is now in the URL and anyone can craft the page; the session keeps the message server-controlled.

## Not covered

CSRF protection for this form (problems 17 and 18).
