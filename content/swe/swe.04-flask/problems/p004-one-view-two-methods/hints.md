## Hint 1

The starter route only lists the default method. Which argument of `@app.route(...)` says which HTTP methods the function accepts?

## Hint 2

`request.method` tells you which method arrived; `request.form.get("name", "")` reads the field without raising an error when it is missing. `markupsafe.escape` (or a template) escapes the text.

## Hint 3

```text
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name: return "Name is required", 400
        return "Thanks, " + escape(name) + "!"
    return the form
```
