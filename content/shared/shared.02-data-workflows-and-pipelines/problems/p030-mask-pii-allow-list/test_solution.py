import copy

import pytest

from solution import mask_email, prepare_export, select_columns


@pytest.mark.parametrize("email, expected", [
    ("asha@example.com", "a***@example.com"),
    ("ravi.kumar@example.com", "r***@example.com"),
    ("x@shop.test", "x***@shop.test"),
])
def test_mask_keeps_first_letter_and_domain(email, expected):
    got = mask_email(email)
    assert got == expected, (
        f"mask_email({email!r}) gave {got!r}, expected {expected!r}: first letter, then exactly "
        "three stars, then '@' and the domain."
    )


def test_mask_does_not_reveal_the_length():
    a = mask_email("al@example.com")
    b = mask_email("alexandra.longname@example.com")
    assert a == b == "a***@example.com", (
        f"Got {a!r} and {b!r}. Always use exactly three stars; one star per hidden letter tells "
        "a reader how long the name is, which helps to guess it."
    )


def test_mask_normalises_case_and_spaces():
    got = mask_email("  Meera@Example.COM ")
    assert got == "m***@example.com", (
        f"Got {got!r}. Strip spaces and lower-case the address first, so the same person always "
        "gets the same mask."
    )


def test_mask_uses_the_last_at_sign():
    got = mask_email('"odd@name"@example.com')
    assert got.endswith("@example.com") and got.startswith('"***'), (
        f"Got {got!r}. The domain is after the LAST '@' (use rpartition)."
    )


@pytest.mark.parametrize("bad", ["not-an-email", "@example.com", "asha@", "", "   "])
def test_malformed_values_are_fully_masked(bad):
    got = mask_email(bad)
    assert got == "***", (
        f"mask_email({bad!r}) gave {got!r}. A value that is not a valid address could be anything "
        "(a phone number, a name typed in the wrong box). Hide it completely: '***'."
    )


def test_none_stays_none():
    assert mask_email(None) is None, "A missing email stays missing (None), it is not masked to '***'."


def test_select_columns_keeps_only_allowed_in_allowed_order():
    row = {"id": 1, "email": "asha@example.com", "city": "Pune", "amount": "19.99"}
    got = select_columns(row, ["amount", "id"])
    assert got == {"amount": "19.99", "id": 1}, f"Got {got}."
    assert list(got) == ["amount", "id"], (
        f"Keys are in the order {list(got)}; use the order of the allow-list so exports have a "
        "stable column order."
    )


def test_select_columns_skips_allowed_names_the_row_does_not_have():
    got = select_columns({"id": 1}, ["id", "city"])
    assert got == {"id": 1}, (
        f"Got {got}. An allowed column that is missing from the row is simply skipped (no KeyError, "
        "no invented None)."
    )


def test_new_source_columns_are_dropped_by_default():
    # The API started sending phone numbers yesterday. Nobody updated the export.
    rows = [{"id": 1, "email": "asha@example.com", "phone": "+91 98xxxxxx01", "city": "Pune"}]
    got = prepare_export(rows, ["id", "city"])
    assert got == [{"id": 1, "city": "Pune"}], (
        f"Got {got}. Use an ALLOW-list: keep only the named columns. A deny-list ('drop email') "
        "silently lets every new sensitive column through."
    )


def test_export_masks_email_when_it_is_allowed():
    rows = [
        {"id": 1, "email": "asha@example.com", "city": "Pune"},
        {"id": 2, "email": None, "city": None},
        {"id": 3, "email": "broken", "city": "Goa"},
    ]
    got = prepare_export(rows, ["id", "email"])
    assert got == [
        {"id": 1, "email": "a***@example.com"},
        {"id": 2, "email": None},
        {"id": 3, "email": "***"},
    ], f"Got {got}. Keep allowed columns, then mask the email column."


def test_export_does_not_change_the_input():
    rows = [{"id": 1, "email": "asha@example.com", "city": "Pune"}]
    before = copy.deepcopy(rows)
    out = prepare_export(rows, ["id", "email"])
    assert rows == before, (
        "prepare_export changed the input rows. Build new dicts; other parts of the pipeline may "
        "still need the original data (for example to pseudonymise it for the warehouse)."
    )
    assert out[0] is not rows[0], "Return new dicts, not the same objects."


def test_empty_input():
    assert prepare_export([], ["id"]) == []
    assert select_columns({"id": 1}, []) == {}, "An empty allow-list allows nothing."
