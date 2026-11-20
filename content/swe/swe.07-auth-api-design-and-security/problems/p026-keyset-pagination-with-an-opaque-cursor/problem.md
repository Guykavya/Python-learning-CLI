# Keyset pagination with an opaque cursor

Chapter sections 10.2 and 10.3. "Skip N rows" (offset) paging breaks when rows arrive while a client is reading: the whole list shifts and a row appears twice. **Keyset** paging says instead "give me the rows **after this one**". The client sends back a **cursor**, an opaque text that holds the sort key of the last row it saw.

Write three functions in `solution.py`. Rows are dictionaries with integer fields `id` and `created` (plus anything else). The list is **newest first**: sorted by the pair `(created, id)`, descending. The id breaks ties, so the order is total and stable.

- `encode_cursor(created: int, row_id: int) -> str`: the JSON `{"created": ..., "id": ...}` (compact), as **base64url without `=` padding**.
- `decode_cursor(cursor: str) -> (created, id)`: the reverse; the input comes from the network, so it may be anything. Raise **`ValueError`** (the API would answer 400) for: text that is not valid base64, not valid JSON, JSON that is not an object with exactly the integer fields `created` and `id` (booleans, floats, strings, a missing or extra key are all wrong). It must accept the cursor with or without padding, and must never raise any other exception type.
- `page_after(rows, cursor=None, limit=3) -> {"items": [...], "next_cursor": str | None}`: sort a **copy** of `rows` (never change the caller's list), keep only the rows strictly **older** than the cursor position `(created, id)` (all rows when `cursor` is `None`), return the first `limit` of them and a `next_cursor` for the last returned row **only if more rows remain**. `limit` below 1 raises `ValueError`.

## Example

```python
rows = [{"id": i, "created": 1000 + i * 10} for i in range(1, 8)]     # ids 1..7
p1 = page_after(rows, None, 3)       # items ids [7, 6, 5]; next_cursor encodes (1050, 5)
rows.append({"id": 100, "created": 5000})     # a new row arrives
p2 = page_after(rows, p1["next_cursor"], 3)   # items ids [4, 3, 2]: no repeat, no skip
decode_cursor("not-a-cursor")        # ValueError
```

## Notes

- Fetching one row more than `limit` is how you learn whether another page exists without counting everything.
- The cursor is not a secret. If clients must not be able to forge one, sign it (chapter 6.4); here a forged cursor only moves the reader to a position.
