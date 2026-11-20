## Hint 1

What tells you "I have already seen everything up to here" in a list that is sorted by `(created, id)`? Why is `created` alone not enough when two rows have the same `created`?

## Hint 2

Python compares tuples element by element, so `(created, id) < (c, i)` does exactly the "strictly older than the cursor" test. For the decoder, list every way the text can be wrong (not base64, not JSON, wrong shape, wrong types) and ask which exceptions the standard library raises; then catch them and raise your own `ValueError`. Remember that `True` is an `int` in Python.

## Hint 3

```text
encode: JSON {"created", "id"} -> bytes -> urlsafe_b64encode -> strip "=" -> str
decode: add "=" until length % 4 == 0 -> urlsafe_b64decode -> json.loads
        check: object with exactly keys created and id, both of type int (not bool) else ValueError
page_after: limit >= 1 else ValueError
            ordered = sorted(rows, key=(created, id), reverse=True)
            if cursor: keep rows with (created, id) < decoded position
            items = ordered[:limit]; more = len(ordered) > limit
            next_cursor = encode(last item) if more else None
```
