# Project: a log analyser

This is the module project. A service writes its log through **two** different libraries, so the
file mixes two line formats, plus tracebacks and other junk. Your job: parse every line you can
into a clean record, and summarise the file.

A sample file is in `fixtures/app.log` next to this problem. Open it and read it before you start.

## Part 1: `LogEntry` and `parse_line`

```python
@dataclass
class LogEntry:
    timestamp: str     # always "YYYY-MM-DD HH:MM:SS"
    level: str         # always one of DEBUG INFO WARNING ERROR CRITICAL
    module: str
    message: str
```

Write `parse_line(line: str) -> LogEntry | None`. Strip the line first (it may end with `\n`
or spaces). Two formats are accepted; anything else returns `None`.

**Format A**

```text
2025-03-01 09:01:16,001 ERROR [payments] Card declined for order 17
```

- date `YYYY-MM-DD`, **one** space, time `HH:MM:SS`, optionally followed by `,` and exactly 3
  digits of milliseconds (dropped from the result);
- one or more spaces, the level, one or more spaces;
- the module in square brackets: `[` + letters, digits, `_` or `.` (at least one) + `]`;
- then optionally one or more spaces and the message (everything up to the end of the line).

**Format B**

```text
[2025-03-01T09:01:17] WARN payments: Retry failed for order 17
```

- `[` date `T` time `]` (no milliseconds in this format);
- one or more spaces, the level, one or more spaces;
- the module (same characters as above) directly followed by `:`;
- then optionally one or more spaces and the message.

**Normalising**

- `timestamp` is `"YYYY-MM-DD HH:MM:SS"` for both formats (space, not `T`; no milliseconds).
- The level is accepted in any case (`error`, `Error`, `ERROR`) and stored in upper case.
  Accepted levels: `DEBUG`, `INFO`, `WARNING`, `WARN`, `ERROR`, `CRITICAL`. `WARN` is stored as
  `WARNING`. Any other word (like `VERBOSE`) makes the line invalid.
- `message` is stripped; it is `""` when there is no message.
- Dates and times are checked for **shape** only (the right number of digits), not for whether
  the date exists. `2025-3-01` (one-digit month) is invalid.

## Part 2: `summarise`

Write `summarise(path) -> dict`. `path` may be a `str` or a `pathlib.Path`; read the file as
UTF-8. Lines are numbered from 1. Return a dict with exactly these keys:

| key | value |
|---|---|
| `"total"` | number of lines that parsed |
| `"levels"` | dict: level → count, only for levels that appear |
| `"top_error_modules"` | list of up to 3 `(module, count)` tuples, counting **only `ERROR`** entries (not `CRITICAL`), highest count first, ties by module name A→Z |
| `"unparsed"` | list of the line numbers of lines that are **not blank** and do not parse |

Blank lines (empty or only whitespace) are neither parsed nor reported.

**Example**

```python
parse_line("2025-03-01 09:01:16,001 error [payments]  Card declined  \n")
# LogEntry(timestamp='2025-03-01 09:01:16', level='ERROR', module='payments', message='Card declined')

parse_line("[2025-03-01T09:02:01] WARN db.pool: Reconnecting")
# LogEntry(timestamp='2025-03-01 09:02:01', level='WARNING', module='db.pool', message='Reconnecting')

parse_line("Traceback (most recent call last):")
# None
```

For a file with these four lines

```text
2025-03-01 09:00:01 INFO [app] start
[2025-03-01T09:00:02] ERROR db: down

oops
```

`summarise` returns

```python
{'total': 2, 'levels': {'INFO': 1, 'ERROR': 1},
 'top_error_modules': [('db', 1)], 'unparsed': [4]}
```

Tips: write each format as a `re.VERBOSE` pattern with **named groups**, compile both once at
module level, and try them in turn with `fullmatch`.
