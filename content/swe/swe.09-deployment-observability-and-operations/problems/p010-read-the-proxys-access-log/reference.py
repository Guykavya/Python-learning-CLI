import json

REQUIRED = ("request_id", "method", "uri", "status", "duration")


def parse_access_line(line):
    try:
        data = json.loads(line)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"not JSON: {exc}") from None
    if not isinstance(data, dict):
        raise ValueError("an access line is a JSON object")
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        raise ValueError(f"missing {', '.join(missing)}")
    upstream_status = str(data.get("upstream_status") or "-")
    tries = 0 if upstream_status.strip() in ("", "-") else len(upstream_status.split(","))
    return {"request_id": data["request_id"], "method": data["method"], "uri": data["uri"],
            "status": int(data["status"]), "duration": float(data["duration"]),
            "upstream_status": upstream_status, "upstream_tries": tries}


def summarise(lines):
    entries, skipped = [], 0
    for line in lines:
        if not line.strip():
            continue
        try:
            entries.append(parse_access_line(line))
        except (ValueError, TypeError):
            skipped += 1
    by_status = {}
    for entry in entries:
        by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
    slowest = sorted(entries, key=lambda e: (-e["duration"], e["request_id"]))[:3]
    errors = sum(1 for e in entries if 500 <= e["status"] <= 599)
    return {
        "requests": len(entries),
        "skipped": skipped,
        "by_status": by_status,
        "slowest": [{"request_id": e["request_id"], "uri": e["uri"], "duration": e["duration"]} for e in slowest],
        "share_5xx": errors / len(entries) if entries else 0.0,
    }
