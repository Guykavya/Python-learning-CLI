## Hint 1

What type does `request.args.get("page")` return for `?page=2`? And what does `get("page", 1, type=int)` return for `?page=abc`?

## Hint 2

With `type=int`, a value that cannot be converted gives the **default**. After that you only need to fix numbers that are converted but out of range (`0`, `-3`): use `max(...)` and `min(...)`.

## Hint 3

```text
page     = max(1, args.get("page", 1, type=int))
per_page = min(100, max(1, args.get("per_page", 20, type=int)))
offset   = (page - 1) * per_page
return jsonify(page=page, per_page=per_page, offset=offset)
```
