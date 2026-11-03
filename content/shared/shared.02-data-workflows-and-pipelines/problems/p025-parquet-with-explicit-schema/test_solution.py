from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from solution import read_orders, write_orders

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))


def order(id, city="Pune", status="shipped", amount="19.99", created=None):
    return {
        "id": id,
        "city": city,
        "status": status,
        "amount": Decimal(amount),
        "created_at": created or datetime(2024, 6, 1, 10, 0, tzinfo=UTC),
    }


EXPECTED_TYPES = {
    "id": pa.int64(),
    "city": pa.string(),
    "status": pa.string(),
    "amount": pa.decimal128(10, 2),
    "created_at": pa.timestamp("us", tz="UTC"),
}


def test_round_trip_keeps_values(tmp_path):
    rows = [order(101), order(102, city=None, status="pending", amount="250.00")]
    path = tmp_path / "orders.parquet"
    assert write_orders(rows, path) == 2, "write_orders must return the number of rows written."
    back = read_orders(path)
    assert back == rows, (
        f"Read back {back}, wrote {rows}. A Parquet round trip with the right schema must give "
        "the same values back."
    )


def test_file_schema_is_exactly_the_contract(tmp_path):
    path = tmp_path / "orders.parquet"
    write_orders([order(101)], path)
    schema = pq.read_schema(path)
    assert schema.names == list(EXPECTED_TYPES), (
        f"Columns are {schema.names}; they must be exactly {list(EXPECTED_TYPES)} in this order."
    )
    for name, expected in EXPECTED_TYPES.items():
        actual = schema.field(name).type
        assert actual == expected, (
            f"Column {name!r} has type {actual}, expected {expected}. Pass schema=... to "
            "pa.Table.from_pylist instead of letting pyarrow guess from the values."
        )


def test_nullability_follows_the_contract(tmp_path):
    path = tmp_path / "orders.parquet"
    write_orders([order(101)], path)
    schema = pq.read_schema(path)
    for name in ("id", "status", "amount", "created_at"):
        assert schema.field(name).nullable is False, (
            f"Column {name!r} must be declared nullable=False in the schema."
        )
    assert schema.field("city").nullable is True, "city may be missing, so it stays nullable."


def test_all_null_column_still_has_string_type(tmp_path):
    path = tmp_path / "orders.parquet"
    write_orders([order(101, city=None), order(102, city=None)], path)
    city_type = pq.read_schema(path).field("city").type
    assert city_type == pa.string(), (
        f"city became {city_type}. When every value in the batch is None, an inferred schema "
        "gives type null. The explicit schema must keep it a string column."
    )


def test_decimal_scale_comes_from_the_schema(tmp_path):
    path = tmp_path / "orders.parquet"
    write_orders([order(101, amount="19.9"), order(102, amount="7")], path)
    amounts = [r["amount"] for r in read_orders(path)]
    assert all(type(a) is Decimal for a in amounts), (
        f"Amounts came back as {[type(a).__name__ for a in amounts]}. Money must stay Decimal "
        "(decimal128), never float."
    )
    assert [str(a) for a in amounts] == ["19.90", "7.00"], (
        f"Amounts read back as {[str(a) for a in amounts]}. decimal128(10, 2) always stores "
        "two decimal places, so 19.9 comes back as 19.90."
    )


def test_offsets_are_converted_to_utc(tmp_path):
    path = tmp_path / "orders.parquet"
    created = datetime(2024, 6, 1, 10, 0, tzinfo=IST)
    write_orders([order(101, created=created)], path)
    back = read_orders(path)[0]["created_at"]
    assert back == created, "The instant must not change: 10:00 at +05:30 is 04:30 UTC."
    assert back.utcoffset() == timedelta(0), (
        f"Read back with offset {back.utcoffset()}. The column type is timestamp(tz='UTC'), so "
        "every value comes back in UTC."
    )
    assert (back.hour, back.minute) == (4, 30), f"Expected 04:30 UTC, got {back.time()}."


def test_naive_datetime_is_rejected_before_writing(tmp_path):
    path = tmp_path / "orders.parquet"
    rows = [order(101), order(102, created=datetime(2024, 6, 1, 10, 0))]
    with pytest.raises(ValueError):
        write_orders(rows, path)
    assert not path.exists(), (
        "A naive datetime was found, so nothing may be written. Check every row BEFORE "
        "pq.write_table; pyarrow itself would silently treat it as UTC."
    )


def test_empty_batch_writes_an_empty_file_with_the_schema(tmp_path):
    path = tmp_path / "empty.parquet"
    assert write_orders([], path) == 0, "An empty batch writes 0 rows."
    table = pq.read_table(path)
    assert table.num_rows == 0
    assert table.schema.field("amount").type == pa.decimal128(10, 2), (
        "Even an empty file must carry the full schema; pa.Table.from_pylist([], schema=...) does that."
    )
    assert read_orders(path) == [], "Reading an empty file gives an empty list."


def test_creates_parent_folders(tmp_path):
    path = tmp_path / "lake" / "orders" / "2024-06-01.parquet"
    write_orders([order(101)], path)
    assert path.exists(), "Create missing parent folders (Path.mkdir(parents=True, exist_ok=True))."


def test_too_many_decimal_places_is_an_error_not_rounding(tmp_path):
    with pytest.raises(pa.ArrowInvalid):
        write_orders([order(101, amount="1.005")], tmp_path / "x.parquet")
    # Do not round amounts yourself: losing a fraction of a rupee silently is a data bug.


def test_missing_required_value_is_an_error(tmp_path):
    with pytest.raises((pa.ArrowInvalid, ValueError, TypeError)):
        write_orders([order(101), {**order(102), "id": None}], tmp_path / "x.parquet")
    # id is nullable=False: pyarrow refuses to write a null id.


def test_read_returns_plain_python_types(tmp_path):
    path = tmp_path / "orders.parquet"
    write_orders([order(5, amount="0.50", created=datetime(2023, 12, 31, 23, 59, tzinfo=UTC))], path)
    row = read_orders(path)[0]
    assert type(row) is dict, "read_orders must return plain dicts (table.to_pylist())."
    assert type(row["id"]) is int and type(row["status"]) is str
    assert type(row["created_at"]) is datetime
    assert row == order(5, amount="0.50", created=datetime(2023, 12, 31, 23, 59, tzinfo=UTC))
