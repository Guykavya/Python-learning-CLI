See the model answer shown when you check. The ideas that must appear:

1. A naive local time loses the offset. On the fall-back night one wall time means two instants (sorting and ranges break, an 8-hour shift is really 9). On the spring-forward night an hour does not exist (a row at 01:30 is impossible, the shift is 7 hours).
2. Python guesses for naive values: `.astimezone()` uses the computer's zone (machine-dependent bugs); naive vs aware comparison raises `TypeError` and stripping `tzinfo` hides the problem; same-zone subtraction is wall-clock.
3. Convert to aware UTC on input, store ISO strings with offset (or timestamps), compute in UTC, convert to the user's `ZoneInfo` only for display.
4. Future local-time events: store wall time + zone name, compute UTC later, because DST rules can change. UTC is right for past events.
