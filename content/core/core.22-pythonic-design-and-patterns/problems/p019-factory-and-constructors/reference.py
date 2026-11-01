import json
from dataclasses import dataclass

EXPORTERS = {}


def register_exporter(fmt):
    def decorator(cls):
        EXPORTERS[fmt] = cls
        return cls
    return decorator


@register_exporter("json")
class JsonExporter:
    def export(self, rows):
        return json.dumps(rows, sort_keys=True)


@register_exporter("csv")
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
    try:
        cls = EXPORTERS[fmt]
    except KeyError:
        known = ", ".join(sorted(EXPORTERS))
        raise ValueError(f"unknown format {fmt!r}; known formats: {known}") from None
    return cls()


@dataclass(frozen=True)
class Money:
    cents: int
    currency: str = "USD"

    @classmethod
    def from_string(cls, text):
        parts = text.split()
        whole, _, frac = parts[0].partition(".")
        cents = int(whole) * 100 + int((frac + "00")[:2])
        currency = parts[1] if len(parts) > 1 else "USD"
        return cls(cents, currency)

    @classmethod
    def from_dict(cls, data):
        return cls(data["cents"], data.get("currency", "USD"))
