## Hint 1

Do not rewrite everything at once. Start by listing what the legacy `go()` does in order:
(1) open and read a file, (2) turn text into records and bad lines, (3) print a summary,
(4) read commands, (5) compute an answer for each, (6) print it. Which of these are
*calculations* (no outside world) and which are *I/O*? Calculations become pure functions that
return strings or lists; I/O stays in `main`.

Good first step: make a copy of the 8 test scripts' idea. Run the legacy script by hand on the
sample file and compare after every change.

## Hint 2

Suggested order, running the tests after each step:

```
1. Record dataclass + parse_records(text) -> (records, bad_lines)       # no I/O, no globals
2. one function per command:  (records, args, today) -> list of lines   # @register_command("list") ...
3. build_report(records, today) -> str                                  # reuse it in the report command
4. run_session(records, read, write, today):
       loop: read -> split -> quit? -> COMMANDS.get(name) -> write each line
5. main(argv, read, write, today, opener): usage / open / parse / summary / run_session
```

Keep small helpers for the shared pieces: one function that formats a record row (the `list`,
`low` and `find` commands print the same line), one that finds expired records (`expired`
and `report`). `help` can be built from `sorted([*COMMANDS, "quit"])`.
