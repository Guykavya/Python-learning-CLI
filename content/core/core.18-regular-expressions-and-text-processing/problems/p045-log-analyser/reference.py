import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

LEVELS = "DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL"

# Format A:  2025-03-01 09:15:02,123 ERROR [payments] Card declined
FORMAT_A = re.compile(
    rf"""
    (?P<date>\d{{4}}-\d{{2}}-\d{{2}}) \x20 (?P<time>\d{{2}}:\d{{2}}:\d{{2}}) (?:,\d{{3}})?
    \s+ (?P<level>{LEVELS}) \s+
    \[ (?P<module>[\w.]+) \]
    (?: \s+ (?P<message>.*) )?
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Format B:  [2025-03-01T09:15:02] WARN payments: retrying
FORMAT_B = re.compile(
    rf"""
    \[ (?P<date>\d{{4}}-\d{{2}}-\d{{2}}) T (?P<time>\d{{2}}:\d{{2}}:\d{{2}}) \]
    \s+ (?P<level>{LEVELS}) \s+
    (?P<module>[\w.]+) :
    (?: \s+ (?P<message>.*) )?
    """,
    re.VERBOSE | re.IGNORECASE,
)


@dataclass
class LogEntry:
    timestamp: str
    level: str
    module: str
    message: str


def parse_line(line: str) -> LogEntry | None:
    line = line.strip()
    for pattern in (FORMAT_A, FORMAT_B):
        m = pattern.fullmatch(line)
        if m:
            level = m["level"].upper()
            if level == "WARN":
                level = "WARNING"
            return LogEntry(
                timestamp=f"{m['date']} {m['time']}",
                level=level,
                module=m["module"],
                message=(m["message"] or "").strip(),
            )
    return None


def summarise(path) -> dict:
    levels = Counter()
    error_modules = Counter()
    unparsed = []
    total = 0
    text = Path(path).read_text(encoding="utf-8")
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        entry = parse_line(line)
        if entry is None:
            unparsed.append(number)
            continue
        total += 1
        levels[entry.level] += 1
        if entry.level == "ERROR":
            error_modules[entry.module] += 1
    top = sorted(error_modules.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    return {
        "total": total,
        "levels": dict(levels),
        "top_error_modules": top,
        "unparsed": unparsed,
    }
