- **Keeping the group, adding a flag.** `([A-Z]+)+` is the problem itself; no flag makes it fast.
- **Trying to catch the hang with `try/except`.** The regex does not raise; it runs for hours. The remedy is a
  better pattern (or a separate process with a timeout in a pipeline you do not control).
- **Using `match` or `search`.** `"AB-12-34-56 "` and `"x AB-12-34-56"` would pass or fail the wrong way. `fullmatch`.
- **Using `$` with `match` to mean "the end".** `$` also matches before a final newline, so `"AB-12-34-56\n"` would
  pass; `fullmatch` does not accept it.
- **`\d` for digits.** In Python text patterns `\d` also matches digits of other scripts. `[0-9]` is exact. (The tests do
  not check this, but a real data check should.)
- **Returning the match object.** The function returns `True`/`False`.
