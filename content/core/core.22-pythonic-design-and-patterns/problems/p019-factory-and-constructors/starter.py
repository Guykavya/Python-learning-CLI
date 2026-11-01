import json
from dataclasses import dataclass


class JsonExporter:
    def export(self, rows):
        return json.dumps(rows, sort_keys=True)


class CsvExporter:
    def export(self, rows):
        if not rows:
            return ""
        columns = sorted(rows[0])
        lines = [",".join(columns)]
        for row in rows:
            lines.append(",".join(str(row[c]) for c in columns))
        return "\n".join(lines)


def create_exporter(fmt):
    if fmt == "json":
        return JsonExporter()
    elif fmt == "csv":
        return CsvExporter()
    else:
        raise ValueError("bad format")


@dataclass(frozen=True)
class Money:
    cents: int
    currency: str = "USD"


def parse_money(text):
    parts = text.split()
    whole, _, frac = parts[0].partition(".")
    cents = int(whole) * 100 + int((frac + "00")[:2])
    currency = parts[1] if len(parts) > 1 else "USD"
    return Money(cents, currency)
