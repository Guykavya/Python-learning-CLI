# Content negotiation with `Accept`

Chapter section 11.3: the client sends `Accept` with what it can read, and how much it prefers each type (**q-value**, from 0 to 1, default 1). The server offers some types. Write

```python
choose(accept_header, offered)   # -> one of offered, or None
```

`offered` is a list of media types in the **server's order of preference** (`["application/json", "text/html"]`).

Rules:

1. `Accept` is a comma-separated list of ranges, each with optional parameters: `text/html;q=0.9, application/json, */*;q=0.1`. Other parameters (`charset=utf-8`, `level=1`) are ignored. Case does not matter.
2. A range can be exact (`text/html`), a type wildcard (`text/*`) or everything (`*/*`).
3. For an offered type, the q-value comes from the **most specific** range that matches it: exact beats `type/*` beats `*/*`.
4. `q=0` means "**not acceptable**". A type whose q is 0 (or that matches no range) cannot be chosen.
5. Pick the offered type with the **highest q**. On a tie, the **first in `offered`** wins (the server's order).
6. If nothing is acceptable return `None` (the server will send `406 Not Acceptable`). If `accept_header` is `None` or empty, the client accepts anything: return `offered[0]`. If `offered` is empty return `None`.
7. A q-value that is not a number counts as 0 for that range; ignore a range without a `/`.

## Example

```python
choose("text/html, application/json;q=0.5", ["application/json", "text/html"])   # "text/html"
choose("*/*", ["application/json", "text/html"])                                   # "application/json"
choose("text/*;q=0.8, text/html;q=0", ["text/html", "text/plain"])                 # "text/plain"
choose("image/png", ["application/json"])                                          # None
```
