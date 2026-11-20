# Query strings are strings

Chapter section 4.2. Everything in `request.args` is a **string**. In `solution.py` write `create_app()` with `GET /items?page=2&per_page=50` that answers JSON:

```json
{"page": 2, "per_page": 50, "offset": 50}
```

Rules:

- `page` defaults to **1**; it must be an integer **1 or more**. `page=abc`, `page=0`, `page=-3` and an empty `page=` all give **1**.
- `per_page` defaults to **20**; it is clamped to the range **1 to 100** (`500` gives `100`, `0` gives `1`, `-5` gives `1`). `per_page=abc` gives the default 20.
- `offset = (page - 1) * per_page`.
- The numbers in the JSON are **numbers**, not strings.

Use `request.args.get(name, default, type=int)`: with `type=int` an unparsable value gives the default instead of an error.

## Example

```text
/items                    -> {"page": 1, "per_page": 20, "offset": 0}
/items?page=3&per_page=5  -> {"page": 3, "per_page": 5, "offset": 10}
/items?page=abc           -> {"page": 1, ...}
/items?per_page=500       -> {"per_page": 100, ...}
```
