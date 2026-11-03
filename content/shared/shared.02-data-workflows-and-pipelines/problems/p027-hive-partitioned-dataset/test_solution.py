from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq

from solution import read_partition, write_partitioned

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))


def order(id, created, city="Pune", status="shipped", amount="10.00"):
    return {"id": id, "city": city, "status": status, "amount": Decimal(amount), "created_at": created}


ROWS = [
    order(101, datetime(2024, 6, 1, 10, 0, tzinfo=UTC), amount="19.99"),
    order(102, datetime(2024, 6, 1, 11, 0, tzinfo=UTC), city=None, status="pending"),
    order(103, datetime(2024, 6, 2, 9, 0, tzinfo=UTC), city="Delhi"),
    # 01:30 on 2 June in India is 20:00 on 1 June in UTC: it belongs to 2024-06-01.
    order(104, datetime(2024, 6, 2, 1, 30, tzinfo=IST), status="cancelled", amount="0.00"),
    order(105, datetime(2024, 6, 3, 23, 59, tzinfo=UTC), city="Goa", amount="1200.50"),
]


def folders(root):
    return sorted(p.name for p in root.iterdir() if p.is_dir())


def test_returns_the_sorted_days(tmp_path):
    days = write_partitioned(ROWS, tmp_path / "orders")
    assert days == ["2024-06-01", "2024-06-02", "2024-06-03"], (
        f"Returned {days}. Return each distinct order day once, sorted. Order 104 was created at "
        "01:30 +05:30 on 2 June, which is 20:00 UTC on 1 June."
    )


def test_hive_folder_layout(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    assert folders(root) == ["order_date=2024-06-01", "order_date=2024-06-02", "order_date=2024-06-03"], (
        f"Folders are {folders(root)}. Hive-style partitioning names each folder column=value, "
        "here order_date=YYYY-MM-DD, using the UTC date."
    )
    for name in folders(root):
        files = list((root / name).glob("*.parquet"))
        assert files, f"{name} has no .parquet file inside."


def test_partition_column_lives_in_the_folder_not_the_file(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    file = next((root / "order_date=2024-06-01").glob("*.parquet"))
    names = pq.read_schema(file).names
    assert "order_date" not in names, (
        f"The file contains columns {names}. With hive partitioning the partition value is stored "
        "once in the folder name; pq.write_to_dataset removes the column from the files for you."
    )
    assert names == ["id", "city", "status", "amount", "created_at"], f"File columns are {names}."


def test_types_in_the_files_come_from_an_explicit_schema(tmp_path):
    root = tmp_path / "orders"
    # every city on 2 June is None in this batch: an inferred schema would make the column type null
    rows = [order(1, datetime(2024, 6, 2, 8, 0, tzinfo=UTC), city=None, amount="5")]
    write_partitioned(rows, root)
    schema = pq.read_schema(next((root / "order_date=2024-06-02").glob("*.parquet")))
    assert schema.field("city").type == pa.string(), (
        f"city has type {schema.field('city').type}. Build the table with an explicit schema."
    )
    assert schema.field("amount").type == pa.decimal128(10, 2), "amount must be decimal128(10, 2)."
    assert schema.field("created_at").type == pa.timestamp("us", tz="UTC"), (
        "created_at must be timestamp('us', tz='UTC')."
    )


def test_read_one_partition(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    got = read_partition(root, "2024-06-01")
    assert [r["id"] for r in got] == [101, 102, 104], (
        f"2024-06-01 holds ids {[r['id'] for r in got]}; expected [101, 102, 104] sorted by id "
        "(104 is there because of its UTC date)."
    )
    assert got[0] == ROWS[0], f"Row 101 came back as {got[0]}; values must survive unchanged."
    assert got[1]["city"] is None and got[2]["created_at"] == ROWS[3]["created_at"]
    assert [r["id"] for r in read_partition(root, "2024-06-03")] == [105]


def test_rows_have_only_the_five_columns(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    keys = set(read_partition(root, "2024-06-02")[0])
    assert keys == {"id", "city", "status", "amount", "created_at"}, (
        f"Row keys are {sorted(keys)}. Return the five order columns; order_date is the folder."
    )


def test_reads_only_the_requested_partition(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    # Damage a file in ANOTHER partition. Reading 2024-06-01 must not even open it.
    (root / "order_date=2024-06-03" / "broken.parquet").write_bytes(b"this is not parquet")
    got = read_partition(root, "2024-06-01")
    assert [r["id"] for r in got] == [101, 102, 104], (
        "read_partition opened files of other days. Read only the folder order_date=<day> "
        "(or use a filter on order_date so pyarrow prunes the other folders)."
    )


def test_missing_day_gives_empty_list(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    assert read_partition(root, "2024-07-01") == [], "A day with no folder has no orders: return []."


def test_whole_dataset_reads_back_with_the_partition_column(tmp_path):
    root = tmp_path / "orders"
    write_partitioned(ROWS, root)
    table = ds.dataset(root, format="parquet", partitioning="hive").to_table()
    assert table.num_rows == len(ROWS), f"The dataset has {table.num_rows} rows, wrote {len(ROWS)}."
    by_id = {r["id"]: str(r["order_date"]) for r in table.to_pylist()}
    assert by_id == {101: "2024-06-01", 102: "2024-06-01", 103: "2024-06-02",
                     104: "2024-06-01", 105: "2024-06-03"}, f"order_date per id is {by_id}."


def test_empty_batch_writes_nothing(tmp_path):
    root = tmp_path / "orders"
    assert write_partitioned([], root) == [], "No rows means no days."
    assert not root.exists() or folders(root) == [], "An empty batch must not create partition folders."
