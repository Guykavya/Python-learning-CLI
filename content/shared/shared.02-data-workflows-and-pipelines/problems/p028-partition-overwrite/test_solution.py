from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import pytest

from solution import write_day

UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))


def order(id, day, hour=10, amount="10.00", status="shipped", tz=UTC):
    y, m, d = map(int, day.split("-"))
    return {"id": id, "city": "Pune", "status": status, "amount": Decimal(amount),
            "created_at": datetime(y, m, d, hour, 0, tzinfo=tz)}


def day_ids(root, day):
    folder = root / f"order_date={day}"
    return sorted(pq.read_table(folder).column("id").to_pylist())


def snapshot(folder):
    """Every file under a folder with its bytes and modification time."""
    return {p.relative_to(folder): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in sorted(folder.rglob("*")) if p.is_file()}


def test_first_write_creates_the_day(tmp_path):
    root = tmp_path / "orders"
    n = write_day([order(1, "2024-06-01"), order(2, "2024-06-01")], root, "2024-06-01")
    assert n == 2, "write_day returns the number of rows written."
    assert day_ids(root, "2024-06-01") == [1, 2]


def test_rewriting_a_day_replaces_it(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01"), order(2, "2024-06-01")], root, "2024-06-01")
    write_day([order(2, "2024-06-01", amount="99.00"), order(3, "2024-06-01")], root, "2024-06-01")
    assert day_ids(root, "2024-06-01") == [2, 3], (
        f"The day holds ids {day_ids(root, '2024-06-01')} after the re-run. The new rows must "
        "REPLACE the old ones: order 1 is gone and 2 appears once. Plain pq.write_to_dataset adds "
        "a new file next to the old one, so the day doubles."
    )
    amounts = pq.read_table(root / "order_date=2024-06-01").column("amount").to_pylist()
    assert Decimal("99.00") in amounts, "Order 2 must have its new amount after the re-run."


def test_running_the_same_day_twice_gives_the_same_result(tmp_path):
    root = tmp_path / "orders"
    rows = [order(1, "2024-06-01"), order(2, "2024-06-01")]
    write_day(rows, root, "2024-06-01")
    first = pq.read_table(root / "order_date=2024-06-01").to_pylist()
    write_day(rows, root, "2024-06-01")
    second = pq.read_table(root / "order_date=2024-06-01").to_pylist()
    assert second == first, (
        f"After running the same day twice the folder holds {len(second)} rows instead of "
        f"{len(first)}. A re-run must give exactly the same data: that is idempotency."
    )
    files = list((root / "order_date=2024-06-01").glob("*.parquet"))
    assert len(files) == 1, f"The day folder has {len(files)} files; a re-run must not pile up files."


def test_other_days_are_not_touched(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01")], root, "2024-06-01")
    write_day([order(5, "2024-06-02"), order(6, "2024-06-02")], root, "2024-06-02")
    before = snapshot(root / "order_date=2024-06-02")
    write_day([order(7, "2024-06-01")], root, "2024-06-01")
    assert (root / "order_date=2024-06-02").is_dir(), "Rewriting 2024-06-01 deleted 2024-06-02."
    after = snapshot(root / "order_date=2024-06-02")
    assert after == before, (
        "The files of 2024-06-02 changed while rewriting 2024-06-01. Only the folder of the day "
        "being written may change (do not delete or rewrite the whole dataset)."
    )
    assert day_ids(root, "2024-06-01") == [7]


def test_no_leftover_temporary_files(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01")], root, "2024-06-01")
    write_day([order(2, "2024-06-02")], root, "2024-06-02")
    write_day([order(3, "2024-06-01")], root, "2024-06-01")
    names = sorted(p.name for p in root.iterdir())
    assert names == ["order_date=2024-06-01", "order_date=2024-06-02"], (
        f"root contains {names}. Remove your temporary and old folders after the swap."
    )


def test_failed_write_keeps_the_old_day(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01"), order(2, "2024-06-01")], root, "2024-06-01")
    bad = [order(3, "2024-06-01", amount="1.005")]  # does not fit decimal128(10, 2)
    with pytest.raises(pa.ArrowInvalid):
        write_day(bad, root, "2024-06-01")
    assert (root / "order_date=2024-06-01").is_dir(), (
        "The new data failed to convert and the day's folder is gone: the last good data was "
        "deleted before the new data existed. Build (and write) the new data first."
    )
    assert day_ids(root, "2024-06-01") == [1, 2], (
        "The new data failed to convert, and the old day is gone or changed. Build (and write) the "
        "new data BEFORE you remove the old folder, so a failure leaves the last good version."
    )


def test_row_from_another_day_is_refused(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01")], root, "2024-06-01")
    with pytest.raises(ValueError):
        write_day([order(2, "2024-06-01"), order(3, "2024-06-02")], root, "2024-06-01")
    assert day_ids(root, "2024-06-01") == [1], "A refused write must not change the day."
    assert not (root / "order_date=2024-06-02").exists()


def test_day_is_the_utc_date(tmp_path):
    root = tmp_path / "orders"
    late_evening_utc = order(8, "2024-06-02", hour=1, tz=IST)   # 2024-06-01 19:30 UTC
    assert write_day([late_evening_utc], root, "2024-06-01") == 1, (
        "01:00 on 2 June at +05:30 is 1 June in UTC. Compare the UTC date with the day."
    )
    with pytest.raises(ValueError):
        write_day([late_evening_utc], root, "2024-06-02")


def test_empty_rows_remove_the_day(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01")], root, "2024-06-01")
    write_day([order(2, "2024-06-02")], root, "2024-06-02")
    assert write_day([], root, "2024-06-01") == 0
    assert not (root / "order_date=2024-06-01").exists(), (
        "Re-running a day that now has no orders must leave no data for that day."
    )
    assert day_ids(root, "2024-06-02") == [2]
    assert write_day([], root, "2024-06-09") == 0, "Emptying a day that never existed is fine."


def test_dataset_reads_back_correctly(tmp_path):
    root = tmp_path / "orders"
    write_day([order(1, "2024-06-01"), order(2, "2024-06-01")], root, "2024-06-01")
    write_day([order(3, "2024-06-02")], root, "2024-06-02")
    write_day([order(2, "2024-06-01")], root, "2024-06-01")
    table = ds.dataset(root, format="parquet", partitioning="hive").to_table()
    got = sorted((r["id"], str(r["order_date"])) for r in table.to_pylist())
    assert got == [(2, "2024-06-01"), (3, "2024-06-02")], f"The whole dataset reads as {got}."
    assert table.schema.field("amount").type == pa.decimal128(10, 2)
