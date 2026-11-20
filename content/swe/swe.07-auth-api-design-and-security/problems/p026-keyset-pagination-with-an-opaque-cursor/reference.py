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
    ordered = sorted(rows, key=lambda r: (r["created"], r["id"]), reverse=True)      # newest first
    if cursor is not None:
        position = decode_cursor(cursor)
        ordered = [r for r in ordered if (r["created"], r["id"]) < position]
    items = ordered[:limit]
    has_more = len(ordered) > limit
    next_cursor = encode_cursor(items[-1]["created"], items[-1]["id"]) if has_more else None
    return {"items": items, "next_cursor": next_cursor}
