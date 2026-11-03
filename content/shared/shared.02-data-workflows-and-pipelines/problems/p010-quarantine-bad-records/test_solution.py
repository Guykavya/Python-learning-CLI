import copy
import json
from decimal import Decimal

import pytest

from solution import process_batch


def check(record):
    errors = []
    for field in ("id", "amount"):
        if field not in record:
            errors.append(f"{field}: missing")
        elif record[field] is None:
            errors.append(f"{field}: null")
    return errors


class Transform:
    """Counts its calls. Raises InvalidOperation for '12,00', ValueError for negative amounts,
    KeyError when 'status' is missing."""

    def __init__(self):
        self.calls = 0

    def __call__(self, record):
        self.calls += 1
        amount = Decimal(record["amount"])
        if amount < 0:
            raise ValueError(f"negative amount {amount}")
        return {"id": record["id"], "amount": amount, "status": record["status"]}


def read_lines(path):
    text = path.read_text(encoding="utf-8")
    assert text.endswith("\n"), "End every JSON Lines record with a newline (also the last one)."
    return [json.loads(line) for line in text.splitlines()]


def rec(i, amount="10.00", status="shipped", **extra):
    return {"id": i, "amount": amount, "status": status, **extra}


def test_all_good_no_file(tmp_path):
    path = tmp_path / "q" / "orders.jsonl"
    result = process_batch([rec(1), rec(2, "5.50")], check, Transform(), path, "run-1")
    assert result == {"good": [{"id": 1, "amount": Decimal("10.00"), "status": "shipped"},
                               {"id": 2, "amount": Decimal("5.50"), "status": "shipped"}],
                      "total": 2, "ok": 2, "quarantined": 0}, f"Result was {result}."
    assert not path.exists(), "No bad records: do not create the quarantine file (an empty file looks like a problem)."


def test_check_errors_are_quarantined_and_transform_not_called(tmp_path):
    path = tmp_path / "orders.jsonl"
    transform = Transform()
    result = process_batch([{"id": 5, "status": "shipped"}, {"id": None, "amount": None}], check, transform, path, "run-2")
    assert result["ok"] == 0 and result["quarantined"] == 2 and result["total"] == 2
    assert transform.calls == 0, (
        f"transform was called {transform.calls} times for records that failed the check. "
        "A record with check errors goes to quarantine without being transformed."
    )
    lines = read_lines(path)
    assert lines == [
        {"run_id": "run-2", "reason": "amount: missing", "record": {"id": 5, "status": "shipped"}},
        {"run_id": "run-2", "reason": "id: null; amount: null", "record": {"id": None, "amount": None}},
    ], f"Quarantine lines were {lines}. Each line: run_id, reason ('; '.join(errors)), original record."


def test_transform_exceptions_of_any_type_are_caught(tmp_path):
    path = tmp_path / "orders.jsonl"
    records = [rec(1), rec(2, "12,00"), rec(3, "-1.00"), {"id": 4, "amount": "2.00"}, rec(5, "3.00")]
    result = process_batch(records, check, Transform(), path, "run-3")
    assert [row["id"] for row in result["good"]] == [1, 5], (
        f"Good ids were {[row['id'] for row in result['good']]}. One bad record must not stop the batch: "
        "records after it are still processed."
    )
    reasons = [line["reason"] for line in read_lines(path)]
    assert reasons[0].startswith("InvalidOperation"), (
        f"Reason was {reasons[0]!r}. decimal.InvalidOperation is NOT a ValueError (it is an ArithmeticError): "
        "catch Exception, and write type(error).__name__ in the reason."
    )
    assert reasons[1] == "ValueError: negative amount -1.00", f"Reason was {reasons[1]!r}; use f'{{type(e).__name__}}: {{e}}'."
    assert reasons[2] == "KeyError: 'status'", f"Reason was {reasons[2]!r}."
    assert result["quarantined"] == 3 and result["ok"] == 2 and result["total"] == 5


def test_non_dict_records(tmp_path):
    path = tmp_path / "orders.jsonl"
    result = process_batch([None, "oops", [1, 2], rec(9)], check, Transform(), path, "run-4")
    assert result["ok"] == 1 and result["quarantined"] == 3
    lines = read_lines(path)
    assert [line["reason"] for line in lines] == ["not an object"] * 3, (
        "A record that is not a dict (null, a string, a list) is quarantined with reason 'not an object' "
        "before check() is called (check would crash on it)."
    )
    assert [line["record"] for line in lines] == [None, "oops", [1, 2]], "Store the original value as 'record'."


def test_appends_across_runs(tmp_path):
    path = tmp_path / "orders.jsonl"
    process_batch([{"id": 1}], check, Transform(), path, "run-a")
    process_batch([rec(2), {"id": 3}], check, Transform(), path, "run-b")
    lines = read_lines(path)
    assert [(line["run_id"], line["record"]["id"]) for line in lines] == [("run-a", 1), ("run-b", 3)], (
        f"Lines were {lines}. Open the file in append mode ('a'): the second run must not erase the first run's records."
    )


def test_creates_missing_parent_folders(tmp_path):
    path = tmp_path / "quarantine" / "2024-06-01" / "orders.jsonl"
    process_batch([{"id": 1}], check, Transform(), path, "run-5")
    assert path.exists(), "Create the parent folders with path.parent.mkdir(parents=True, exist_ok=True)."


def test_original_record_is_kept_unchanged_and_unicode_survives(tmp_path):
    path = tmp_path / "orders.jsonl"
    bad = {"id": 7, "amount": "1,50", "status": "shipped", "customer": {"name": "Zoë Fernandes", "city": "Panaji"}}
    before = copy.deepcopy(bad)
    process_batch([bad], check, Transform(), path, "run-6")
    assert bad == before, "Do not change the input record."
    assert read_lines(path)[0]["record"] == before, (
        "The quarantined 'record' must be the original raw record, so it can be fixed and re-processed later."
    )


def test_each_line_is_one_json_object(tmp_path):
    path = tmp_path / "orders.jsonl"
    process_batch([{"id": 1}, {"id": 2}, {"id": 3}], check, Transform(), path, "run-7")
    raw = path.read_text(encoding="utf-8").splitlines()
    assert len(raw) == 3, (
        f"The file has {len(raw)} lines for 3 bad records. JSON Lines means exactly one json.dumps(...) per line "
        "(no indent=, no one big list)."
    )


def test_keyboard_interrupt_is_not_swallowed(tmp_path):
    def transform(record):
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        process_batch([rec(1)], check, transform, tmp_path / "orders.jsonl", "run-8")
    # A bare 'except:' or 'except BaseException' would quarantine Ctrl+C as a bad record.


def test_empty_batch(tmp_path):
    path = tmp_path / "orders.jsonl"
    assert process_batch([], check, Transform(), path, "run-9") == {"good": [], "total": 0, "ok": 0, "quarantined": 0}
    assert not path.exists()
