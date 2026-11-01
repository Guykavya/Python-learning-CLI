"""Inventory tool: pure core + a thin I/O shell (main)."""
from dataclasses import dataclass
from datetime import date

LOW_STOCK_LIMIT = 5
COMMANDS = {}


@dataclass(frozen=True)
class Record:
    sku: str
    name: str
    qty: int
    price: float
    expires: date | None = None

    @property
    def value(self):
        return self.qty * self.price


def register_command(name):
    def decorator(func):
        COMMANDS[name] = func
        return func
    return decorator


# ---- parsing (pure) -------------------------------------------------------

def _parse_line(line):
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 5:
        raise ValueError("expected 5 fields")
    sku, name, qty, price, expires = parts
    expires_on = date.fromisoformat(expires) if expires else None
    record = Record(sku, name, int(qty), float(price), expires_on)
    if record.qty < 0 or record.price < 0:
        raise ValueError("negative number")
    return record


def parse_records(text):
    records, bad_lines = [], []
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line or (number == 1 and line.lower().startswith("sku")):
            continue
        try:
            records.append(_parse_line(line))
        except ValueError:
            bad_lines.append(number)
    return records, bad_lines


# ---- reporting (pure) -----------------------------------------------------

def _row_line(record):
    return "%-6s %-12s %4d %8.2f" % (record.sku, record.name, record.qty, record.price)


def _total_value(records):
    return sum(record.value for record in records)


def _expired(records, today):
    return [r for r in records if r.expires is not None and r.expires < today]


def _most_valuable_line(records):
    if not records:
        return "most valuable: none"
    best = min(records, key=lambda r: (-r.value, r.sku))
    return f"most valuable: {best.sku} {best.name} ({best.value:.2f})"


def build_report(records, today):
    low = sorted(r.sku for r in records if r.qty < LOW_STOCK_LIMIT)
    expired = sorted(r.sku for r in _expired(records, today))
    return "\n".join([
        f"INVENTORY REPORT {today.isoformat()}",
        f"items: {len(records)}  units: {sum(r.qty for r in records)}  value: {_total_value(records):.2f}",
        f"low stock (<{LOW_STOCK_LIMIT}): {', '.join(low) or 'none'}",
        f"expired: {', '.join(expired) or 'none'}",
        _most_valuable_line(records),
    ])


# ---- commands (pure: records, args, today -> list of lines) ---------------

@register_command("list")
def cmd_list(records, args, today):
    rows = sorted(records, key=lambda r: r.sku)
    return [_row_line(r) for r in rows] or ["no records"]


@register_command("low")
def cmd_low(records, args, today):
    try:
        limit = int(args[0]) if args else LOW_STOCK_LIMIT
    except ValueError:
        return ["error: low needs a whole number"]
    found = sorted((r for r in records if r.qty < limit), key=lambda r: (r.qty, r.sku))
    return [_row_line(r) for r in found] or ["nothing low on stock"]


@register_command("expired")
def cmd_expired(records, args, today):
    found = sorted(_expired(records, today), key=lambda r: (r.expires, r.sku))
    lines = ["%-6s %-12s expired %s" % (r.sku, r.name, r.expires.isoformat()) for r in found]
    return lines or ["nothing expired"]


@register_command("value")
def cmd_value(records, args, today):
    return [f"total value: {_total_value(records):.2f}"]


@register_command("find")
def cmd_find(records, args, today):
    text = " ".join(args).lower()
    if not text:
        return ["error: find needs some text"]
    found = sorted((r for r in records if text in r.name.lower()), key=lambda r: r.sku)
    return [_row_line(r) for r in found] or ["no match"]


@register_command("report")
def cmd_report(records, args, today):
    return build_report(records, today).splitlines()


@register_command("help")
def cmd_help(records, args, today):
    return ["commands: " + ", ".join(sorted([*COMMANDS, "quit"]))]


# ---- the shell: the only place that talks to the outside world -------------

def run_session(records, read, write, today):
    while True:
        try:
            parts = read("> ").split()
        except EOFError:
            return
        if not parts:
            continue
        name, args = parts[0].lower(), parts[1:]
        if name in ("quit", "exit"):
            write("bye")
            return
        handler = COMMANDS.get(name)
        lines = handler(records, args, today()) if handler else [f"unknown command: {name} (try help)"]
        for text in lines:
            write(text)


def main(argv, read=input, write=print, today=date.today, opener=open):
    if not argv:
        write("usage: inventory FILE")
        return 2
    try:
        with opener(argv[0]) as handle:
            text = handle.read()
    except OSError:
        write(f"error: cannot open {argv[0]}")
        return 1
    records, bad_lines = parse_records(text)
    write(f"loaded {len(records)} records")
    if bad_lines:
        write(f"skipped {len(bad_lines)} bad line(s): " + ", ".join(map(str, bad_lines)))
    run_session(records, read, write, today)
    return 0
