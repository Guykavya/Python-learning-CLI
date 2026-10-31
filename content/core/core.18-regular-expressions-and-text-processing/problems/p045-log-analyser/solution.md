## Approach

**Parse with one pattern per format.** Each format is a `re.VERBOSE` pattern with named groups,
compiled once at module level. Verbose mode lets the pattern read like the format description:

- `\x20` is the single space between date and time (a plain space would be ignored in verbose
  mode);
- `(?:,\d{3})?` makes the milliseconds optional without capturing them;
- `(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)` with `re.IGNORECASE` accepts any case and
  nothing else. Because the level must be followed by `\s+`, `INFORMATION` cannot match `INFO`;
- `\[ (?P<module>[\w.]+) \]` escapes the brackets; `[\w.]+` allows dotted module names;
- `(?: \s+ (?P<message>.*) )?` makes the whole " message" part optional, so its group is `None`
  when there is no message.

`fullmatch` on the stripped line guarantees that every character is explained by the pattern:
junk before or after makes the line invalid. The shape check is done by the regex; the
**normalising** (upper-case, `WARN` → `WARNING`, `T` → space, `None` → `""`) is done in plain
Python afterwards, which keeps the patterns simple.

**Summarise in one pass.** `enumerate(..., start=1)` gives human line numbers. Blank lines are
skipped before parsing. Two `Counter`s collect levels and ERROR modules. Ties in the top list are
broken by name with `sorted(..., key=lambda kv: (-kv[1], kv[0]))`: `Counter.most_common` would
keep first-seen order instead. Converting `levels` to a plain `dict` at the boundary means callers
get normal `KeyError` behaviour.

## Code

```python
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
```

Note the doubled braces `{{4}}` in the `rf"..."` patterns: in an f-string, `{` and `}` are
placeholders, so a literal regex quantifier `{4}` must be written `{{4}}`. Only `{LEVELS}` is a
real placeholder. (Without the `f`, write `\d{4}` normally and join the level list in with `+`.)

## Complexity

O(total characters) for the file: each line is tried against at most two patterns with no nested
quantifiers, so no backtracking blow-up. Sorting the ERROR modules is O(m log m) for m modules.
Memory: the file text plus the counters. For huge logs, iterate over the open file
(`for number, line in enumerate(f, start=1)`) instead of reading it all.

## Another way

- **One combined pattern** with both formats as alternatives: duplicate group names are not
  allowed in one pattern, so the groups would need different names (`date_a`, `date_b`) and the
  code gets messier. Two patterns tried in turn are clearer.
- **A list of `(pattern, normaliser)` pairs**: adding a third log format later is then one more
  entry in the list, and `parse_line` does not change.
- Return a `dataclass` `Summary` instead of a dict for better type checking.
