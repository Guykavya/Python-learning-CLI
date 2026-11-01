# Project: from legacy script to clean module

The warehouse team's `starter.py` is a real-looking legacy script: a global `DATA` list, a
hard-coded file path, `input()` and `print()` everywhere, one 100-line function `go()` and an
`if/elif` chain over the command name. It works. You will turn it into a small clean module
that behaves **exactly the same**, and that you can test without a keyboard, a screen or a disk.

This is the module project. Use everything from the chapter: characterization first, then
small steps, with the tests green at the end of each step.

## What the legacy script does

Run it like `python starter.py inventory.csv` (it asks for commands with a `> ` prompt).
Sample file:

```
sku,name,qty,price,expires
A100,Widget,40,2.50,2025-12-01
B200,Gadget,3,19.99,
C300,Gizmo Pro,0,120.00,2025-01-31
this line is broken
```

Lines are `sku,name,qty,price,expires` (expires may be empty). The first line is skipped if it
starts with `sku`. Blank lines are ignored. A line with the wrong number of fields, a non-number
`qty`/`price`, a bad date, or a negative `qty`/`price` is a **bad line**; its 1-based line
number is remembered. The script prints `loaded N records`, then
`skipped K bad line(s): 7, 8, 9` if there were any, then loops over commands.

| Command | Output |
|---|---|
| `list` | all records sorted by sku, or `no records` |
| `low [N]` | records with `qty < N` (default 5) sorted by qty then sku; `nothing low on stock`; `error: low needs a whole number` |
| `expired` | records whose date is before today, sorted by date then sku; `nothing expired` |
| `value` | `total value: 336.47` |
| `find TEXT` | records whose name contains TEXT (any case), sorted by sku; `no match`; `error: find needs some text` |
| `report` | a 5-line report (see the code) |
| `help` | `commands: expired, find, help, list, low, quit, report, value` |
| `quit` / `exit` | `bye` and stop |
| anything else | `unknown command: xyz (try help)` |

Commands are case-insensitive, blank lines are ignored, and the end of input (`EOFError`) ends the
session. Read the legacy code for the exact formats; the tests contain eight command scripts
whose expected output was **recorded from the legacy script itself**.

## What you deliver

Copy `starter.py` to `solution.py` and rewrite it so that it contains these names:

| Name | Contract |
|---|---|
| `Record` | a `@dataclass` with fields `sku, name, qty, price, expires` (`expires` is a `date` or `None`) |
| `parse_records(text)` | **pure**. Returns `(records, bad_lines)`: a list of `Record` and a list of 1-based line numbers |
| `build_report(records, today)` | **pure**. Returns the report as one string (lines joined with `"\n"`, no trailing newline). `today` is a `date` |
| `COMMANDS` | the registry: a dict from command name to handler. The only allowed module-level mutable object |
| `register_command(name)` | decorator that stores the handler in `COMMANDS` and returns it unchanged |
| handlers | `handler(records, args, today) -> list[str]` (pure; `args` is the list of words after the command; `today` is a `date`). Register `list`, `low`, `expired`, `value`, `find`, `report`, `help` |
| `main(argv, read=input, write=print, today=date.today, opener=open)` | the **only** function that may touch the outside world. Returns an exit code |

Details of `main`:

- `argv` is the list of arguments (without the program name). With no arguments write
  `usage: inventory FILE` and return `2`.
- Read the file with `opener(argv[0])` (use `with`; it returns a file object with `.read()`).
  If that raises `OSError`, write `error: cannot open <path>` and return `1`.
- Write every output line with `write(line)`. Ask for each command with `read("> ")`.
  Call `today()` once per command line and pass the resulting date to the handler.
- `quit` and `exit` are handled by `main`'s loop (not registered), but `help` must still list
  `quit`, and it must list any command registered later.
- Return `0` after a normal session.

**Rules checked by the tests (`ast`)**

- No function is longer than **20 lines**.
- No module-level mutable state except `COMMANDS`, and no `global` statement.
- `print`, `input` and `open` are **called** only inside `main` (and even there you should use the injected ones).
- Nobody calls `date.today()`; `today` comes in as a parameter.
- Commands are registered with `@register_command(...)`; no `if/elif` chain of three or more branches.
- `Record` is decorated with `@dataclass`.

Tests never touch a real keyboard, screen or file. The functions `input`, `open` and `print`
are even replaced by ones that fail if your code calls them.

**Example session** (the tests do this with fakes)

```python
main(["inventory.csv"], read=fake_read, write=lines.append, today=lambda: date(2025, 6, 15), opener=fake_open)
# lines == ["loaded 7 records", "skipped 3 bad line(s): 7, 8, 9", ...]
```
