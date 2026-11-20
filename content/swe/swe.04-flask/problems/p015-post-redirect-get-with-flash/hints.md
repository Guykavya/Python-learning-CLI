## Hint 1

What should the browser's *last request* be after a successful form? If it is the POST, a refresh repeats it. Which HTTP answer makes the browser go and do a GET instead?

## Hint 2

`flash("text")` stores a message in the session; `get_flashed_messages()` (already used by the thanks template) reads **and removes** it. Validate first, collect errors in a dict, and render the form again only when the dict is not empty.

## Hint 3

```text
values = {name, message} each stripped from request.form
errors = {}
if not values["name"]: errors["name"] = "Name is required"
if len(values["message"]) < 10: errors["message"] = "..."
if errors: return render the form with values and errors (200)
store values; flash(f"Thanks, {name}!"); return redirect(url_for("thanks"))
```
