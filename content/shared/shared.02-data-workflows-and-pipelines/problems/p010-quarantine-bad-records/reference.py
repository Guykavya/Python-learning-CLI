import json
from pathlib import Path


def reason_for(record, check, transform):
    """Return (row, None) for a good record or (None, reason) for a bad one."""
    if not isinstance(record, dict):
        return None, "not an object"
    errors = check(record)
    if errors:
        return None, "; ".join(errors)
    try:
        return transform(record), None
    except Exception as error:            # one bad record must not stop the batch
        return None, f"{type(error).__name__}: {error}"


def process_batch(records, check, transform, quarantine_path, run_id):
    """Split records into good rows and quarantined ones (JSON Lines, appended). Never crash on one record."""
    good, bad = [], []
    for record in records:
        row, reason = reason_for(record, check, transform)
        if reason is None:
            good.append(row)
        else:
            bad.append({"run_id": run_id, "reason": reason, "record": record})

    if bad:
        quarantine_path = Path(quarantine_path)
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)
        with quarantine_path.open("a", encoding="utf-8") as f:
            for entry in bad:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {"good": good, "total": len(records), "ok": len(good), "quarantined": len(bad)}
