## Approach

```python
import base64
import json


def encode_cursor(created: int, row_id: int) -> str:
    raw = json.dumps({"created": created, "id": row_id}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_cursor(cursor: str):
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        created, row_id = data["created"], data["id"]
        if type(created) is not int or type(row_id) is not int or set(data) != {"created", "id"}:
            raise TypeError
        return created, row_id
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ValueError("invalid cursor") from None


def page_after(rows, cursor=None, limit=3):
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer")
    ordered = sorted(rows, key=lambda r: (r["created"], r["id"]), reverse=True)      # a copy, newest first
    if cursor is not None:
        position = decode_cursor(cursor)
        ordered = [r for r in ordered if (r["created"], r["id"]) < position]
    items = ordered[:limit]
    has_more = len(ordered) > limit
    next_cursor = encode_cursor(items[-1]["created"], items[-1]["id"]) if has_more else None
    return {"items": items, "next_cursor": next_cursor}
```

Why it works: the cursor stores a **position** in the sort order, not a count. A row inserted at the front, or deleted anywhere, changes nothing about "everything older than `(1050, 5)`". Offset paging stores a count ("skip 3"), and a count shifts whenever the list changes (chapter 10.2). The pair `(created, id)` is unique, so rows with the same `created` are never skipped on a page boundary. In the decoder, many things can go wrong (`binascii.Error`, `UnicodeDecodeError` and `json.JSONDecodeError` are all `ValueError` subclasses; `KeyError`, `TypeError` and `AttributeError` are not), and all of them become one `ValueError` that the API turns into 400. `type(x) is int` rejects `True`.

## Complexity

The sketch sorts the whole list: O(n log n) per page. A database does the same with an index on `(created, id)` and `WHERE (created, id) < (?, ?) ORDER BY created DESC, id DESC LIMIT n+1`, which reads only the rows of the page.

## Another way

If the input were already sorted, `bisect` finds the cursor position in O(log n) and a slice returns the page. In SQL, a row-value comparison `WHERE (created, id) < (?, ?)` (SQLite and PostgreSQL) does the same as the tuple comparison here.
