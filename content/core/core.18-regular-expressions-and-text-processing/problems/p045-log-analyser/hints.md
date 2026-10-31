## Hint 1

Do part 1 one format at a time. Write format A as a `re.VERBOSE` pattern with one named group
per field you need later (`date`, `time`, `level`, `module`, `message`). Which parts are optional
(milliseconds, message)? Which characters must be escaped (`[`, `]`)? Test it on the lines of
`fixtures/app.log` by printing `pattern.fullmatch(line)` for each one.

## Hint 2

Both patterns can share one alternation for the level, `DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL`,
with `re.IGNORECASE`. After a match, normalise in Python, not in the regex: upper-case the level,
map `WARN` to `WARNING`, join date and time with a space, turn a `None` message into `""`.

```
FORMAT_A = (?P<date>\d{4}-\d{2}-\d{2}) \x20 (?P<time>\d{2}:\d{2}:\d{2}) (?:,\d{3})?
           \s+ (?P<level>LEVELS) \s+ \[ (?P<module>[\w.]+) \] (?: \s+ (?P<message>.*) )?
FORMAT_B = \[ date T time \] \s+ level \s+ (?P<module>[\w.]+) : (?: \s+ (?P<message>.*) )?

parse_line(line):
    line = line.strip()
    for p in (FORMAT_A, FORMAT_B):
        m = p.fullmatch(line)
        if m: return LogEntry(...normalised...)
    return None
```

## Hint 3

For part 2, one pass over the lines with two `Counter`s:

```
for number, line in enumerate(text.splitlines(), start=1):
    if line is blank: continue
    e = parse_line(line)
    if e is None: unparsed.append(number); continue
    total += 1; levels[e.level] += 1
    if e.level == "ERROR": errors[e.module] += 1
top = sorted(errors.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
return {"total": total, "levels": dict(levels), "top_error_modules": top, "unparsed": unparsed}
```
