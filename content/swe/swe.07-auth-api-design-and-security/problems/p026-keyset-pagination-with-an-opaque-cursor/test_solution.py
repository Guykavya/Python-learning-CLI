import base64
import copy
import json

import pytest

from solution import decode_cursor, encode_cursor, page_after


def b64(raw: bytes, pad=True):
    text = base64.urlsafe_b64encode(raw).decode()
    return text if pad else text.rstrip("=")


def make_rows(n, start=1):
    return [{"id": i, "created": 1000 + i * 10} for i in range(start, start + n)]


def walk(rows, limit, hook=None):
    """Follow next_cursor until the end. `hook(page_number)` may change `rows` between two pages."""
    seen, cursor, n = [], None, 0
    while True:
        page = page_after(rows, cursor, limit)
        seen.extend(r["id"] for r in page["items"])
        n += 1
        assert n < 100, "The cursor never ends: next_cursor must be None when no rows are left."
        if page["next_cursor"] is None:
            return seen
        cursor = page["next_cursor"]
        if hook:
            hook(n)


def test_cursor_round_trip():
    c = encode_cursor(1050, 5)
    assert isinstance(c, str) and decode_cursor(c) == (1050, 5), "decode_cursor(encode_cursor(a, b)) must give (a, b) as a tuple of ints."


def test_cursor_is_url_safe_base64_of_json_without_padding():
    c = encode_cursor(1050, 5)
    assert "=" not in c and "+" not in c and "/" not in c, f"A cursor goes into a URL: base64url without '=' padding, got {c!r}."
    padded = c + "=" * (-len(c) % 4)
    assert json.loads(base64.urlsafe_b64decode(padded)) == {"created": 1050, "id": 5}, 'The cursor is base64url of the JSON {"created": ..., "id": ...}.'


def test_decode_accepts_both_padded_and_unpadded_input():
    raw = json.dumps({"created": 7, "id": 3}).encode()
    assert decode_cursor(b64(raw, pad=True)) == (7, 3)
    assert decode_cursor(b64(raw, pad=False)) == (7, 3), "Add the missing '=' before decoding: base64 needs a length that is a multiple of 4."


@pytest.mark.parametrize("bad", [
    "not-a-cursor",
    "",
    "@@@@",
    b64(b"not json"),
    b64(b"[1, 2]"),
    b64(b'"text"'),
    b64(b"null"),
    b64(b'{"created": 1}'),
    b64(b'{"id": 1}'),
    b64(b'{"created": "1", "id": 2}'),
    b64(b'{"created": 1.5, "id": 2}'),
    b64(b'{"created": true, "id": 2}'),
    b64(b'{"created": 1, "id": null}'),
    b64(b'{"created": 1, "id": 2, "extra": 3}'),
    b64(b"\xff\xfe\xfd"),
])
def test_tampered_cursors_raise_value_error(bad):
    with pytest.raises(ValueError):
        decode_cursor(bad)


def test_page_after_rejects_a_bad_cursor():
    with pytest.raises(ValueError):
        page_after(make_rows(5), "garbage", 2)


@pytest.mark.parametrize("limit", [0, -1])
def test_limit_must_be_positive(limit):
    with pytest.raises(ValueError):
        page_after(make_rows(3), None, limit)


def test_first_page_is_newest_first_with_a_cursor():
    page = page_after(make_rows(7), None, 3)
    assert [r["id"] for r in page["items"]] == [7, 6, 5], f"Newest first: expected ids [7, 6, 5], got {[r['id'] for r in page['items']]}."
    assert decode_cursor(page["next_cursor"]) == (1050, 5), "The cursor is the position of the LAST item of the page (created, id)."


def test_walking_all_pages_gives_every_row_once():
    rows = make_rows(10)
    assert walk(rows, 3) == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]


def test_exactly_full_last_page_has_no_cursor():
    page = page_after(make_rows(6), None, 3)
    page2 = page_after(make_rows(6), page["next_cursor"], 3)
    assert [r["id"] for r in page2["items"]] == [3, 2, 1]
    assert page2["next_cursor"] is None, "No rows are left after this page, so next_cursor is None (look at limit + 1 rows to know)."


def test_empty_and_small_inputs():
    assert page_after([], None, 3) == {"items": [], "next_cursor": None}
    one = page_after(make_rows(1), None, 5)
    assert [r["id"] for r in one["items"]] == [1] and one["next_cursor"] is None


def test_input_order_does_not_matter_and_rows_are_not_modified():
    rows = make_rows(8)
    shuffled = [rows[i] for i in (3, 0, 7, 1, 5, 2, 6, 4)]
    snapshot = copy.deepcopy(shuffled)
    assert walk(shuffled, 3) == [8, 7, 6, 5, 4, 3, 2, 1]
    assert shuffled == snapshot, "page_after must not sort or change the list it was given (use sorted(), not .sort())."


def test_equal_created_values_are_ordered_by_id_and_nothing_is_lost():
    rows = [{"id": i, "created": 500} for i in range(1, 11)]
    assert walk(rows, 3) == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1], (
        "Many rows share one 'created' value. The sort key is the PAIR (created, id), and the cursor compares the pair, "
        "otherwise rows on the boundary are skipped or repeated.")


def test_a_new_row_between_pages_causes_no_repeat_and_no_skip():
    rows = make_rows(9)

    def insert_newest(page_number):
        if page_number == 1:
            rows.append({"id": 100, "created": 5000})            # newest row, arrives after page 1

    ids = walk(rows, 3, hook=insert_newest)
    assert ids == [9, 8, 7, 6, 5, 4, 3, 2, 1], (
        f"Got {ids}. New rows appear at the front; pages already read must not shift. Offset paging would repeat 7 here; "
        "a keyset condition (rows strictly older than the cursor) cannot.")


def test_deleting_the_cursor_row_between_pages_is_harmless():
    rows = make_rows(9)

    def delete_last_seen(page_number):
        if page_number == 1:
            rows[:] = [r for r in rows if r["id"] != 7]           # the last row of page 1 disappears

    ids = walk(rows, 3, hook=delete_last_seen)
    assert ids == [9, 8, 7, 6, 5, 4, 3, 2, 1][:3] + [6, 5, 4, 3, 2, 1], "The cursor is a position, not a row id: it still works when its row is deleted."


def test_a_cursor_forged_by_hand_works_as_a_position():
    rows = make_rows(6)
    c = encode_cursor(1030, 3)                                    # "everything older than id 3"
    assert [r["id"] for r in page_after(rows, c, 5)["items"]] == [2, 1]
