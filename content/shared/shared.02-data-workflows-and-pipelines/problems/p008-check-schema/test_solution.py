import copy

from solution import check_schema

ORDER_SCHEMA = {
    "id": {"type": int, "required": True},
    "status": {"type": str, "required": True},
    "amount": {"type": str, "required": True},
    "city": {"type": str, "required": False},
    "discount": {"type": float, "required": False},
}

GOOD = {"id": 101, "status": "shipped", "amount": "19.99"}


def test_valid_record_has_no_errors():
    assert check_schema(GOOD, ORDER_SCHEMA) == [], "A record with all required fields of the right type is valid: []."
    full = dict(GOOD, city="Pune", discount=0.5)
    assert check_schema(full, ORDER_SCHEMA) == [], "Optional fields with the right type are fine too."


def test_missing_required_field():
    assert check_schema({"id": 1, "status": "shipped"}, ORDER_SCHEMA) == ["amount: missing"], (
        "A required field that is not in the record gives '<field>: missing'."
    )


def test_null_required_field():
    assert check_schema({"id": 1, "status": None, "amount": "1.00"}, ORDER_SCHEMA) == ["status: null"], (
        "A required field that is None gives '<field>: null' (not a type error 'got NoneType')."
    )


def test_optional_missing_or_null_is_fine():
    assert check_schema(dict(GOOD, city=None), ORDER_SCHEMA) == [], (
        "An optional field may be None. Do not report it as null or as a wrong type."
    )
    assert check_schema(GOOD, ORDER_SCHEMA) == [], "An optional field may be missing."


def test_optional_field_with_wrong_type_is_an_error():
    assert check_schema(dict(GOOD, city=411001), ORDER_SCHEMA) == ["city: expected str, got int"], (
        "Optional means 'may be missing or None', not 'anything goes'. A present value is type-checked."
    )


def test_wrong_type_message_uses_type_names():
    assert check_schema({"id": "101", "status": "shipped", "amount": 19.99}, ORDER_SCHEMA) == [
        "id: expected int, got str", "amount: expected str, got float"], (
        "Use the __name__ of the expected type and of type(value): 'expected int, got str'."
    )


def test_bool_is_not_an_int():
    assert check_schema({"id": True, "status": "shipped", "amount": "1"}, ORDER_SCHEMA) == [
        "id: expected int, got bool"], (
        "isinstance(True, int) is True because bool subclasses int. A schema check must reject it: "
        "an id of True is a bug in the source, not order number 1."
    )


def test_bool_accepted_where_schema_says_bool():
    schema = {"paid": {"type": bool, "required": True}}
    assert check_schema({"paid": False}, schema) == [], "False is a valid bool (and is not 'null' or 'missing')."
    assert check_schema({"paid": 0}, schema) == ["paid: expected bool, got int"], "0 is an int, not a bool."


def test_float_field_accepts_int_but_not_bool():
    assert check_schema(dict(GOOD, discount=5), ORDER_SCHEMA) == [], (
        "A float field accepts an int: JSON often writes 5.0 as 5."
    )
    assert check_schema(dict(GOOD, discount=True), ORDER_SCHEMA) == ["discount: expected float, got bool"]
    assert check_schema(dict(GOOD, discount="0.5"), ORDER_SCHEMA) == ["discount: expected float, got str"]


def test_zero_and_empty_string_are_not_null():
    assert check_schema({"id": 0, "status": "", "amount": ""}, ORDER_SCHEMA) == [], (
        "0 and '' are real values. Check 'value is None', not 'if not value'."
    )


def test_unexpected_fields_after_schema_fields_in_record_order():
    record = {"zeta": 1, "id": 1, "status": "x", "amount": "1", "alpha": 2}
    assert check_schema(record, ORDER_SCHEMA) == ["zeta: unexpected field", "alpha: unexpected field"], (
        "Report extra keys after all schema checks, in the order they appear in the record (not sorted)."
    )


def test_many_errors_in_schema_order():
    record = {"coupon": "X", "amount": 19.99, "status": None, "id": "101", "city": None}
    assert check_schema(record, ORDER_SCHEMA) == [
        "id: expected int, got str", "status: null", "amount: expected str, got float",
        "coupon: unexpected field"], (
        "Collect ALL errors (do not stop at the first), in schema order, then the extra fields."
    )


def test_empty_record():
    assert check_schema({}, ORDER_SCHEMA) == ["id: missing", "status: missing", "amount: missing"]


def test_another_schema():
    schema = {"sku": {"type": str, "required": True}, "qty": {"type": int, "required": True},
              "note": {"type": str, "required": False}}
    assert check_schema({"sku": "B1", "qty": 2.0}, schema) == ["qty: expected int, got float"], (
        "An int field does not accept a float (2.0 may really be 2.5 elsewhere)."
    )
    assert check_schema({"qty": None, "note": 3}, schema) == ["sku: missing", "qty: null", "note: expected str, got int"]


def test_record_not_changed():
    record = {"id": None, "extra": [1, 2]}
    before = copy.deepcopy(record)
    check_schema(record, ORDER_SCHEMA)
    assert record == before, "check_schema must only read the record."
