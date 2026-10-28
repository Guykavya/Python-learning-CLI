## Hint 1

Run the starter by hand on the examples and look at what each step returns. What is
`parse_local(...).tzinfo`? What does `.astimezone(timezone.utc)` do when the datetime has no zone?
(The chapter: a naive datetime is read as *this computer's* local time.)

## Hint 2

Bug by bug:
1. `parse_local` must attach the zone without moving the clock: `naive.replace(tzinfo=ZoneInfo(zone))`.
2. Once that is fixed, `to_utc_iso` is right.
3. `shift_hours`: two aware datetimes with the **same** `tzinfo` are subtracted wall clock minus
   wall clock. Where should both be converted first?
4. `is_overdue`: dropping the zones makes 15:00 Kolkata look later than 12:00 UTC. What happens if
   you compare two aware datetimes directly?

## Hint 3

To detect a skipped time, make a round trip: convert the aware value to UTC and back to the zone.
A real wall time comes back unchanged. A skipped one (say 01:30 on 31 March in London) comes back
as a different wall time (02:30), so compare the naive parts.

```
naive = strptime(text, FMT)
local = naive.replace(tzinfo=ZoneInfo(zone))
back  = local.astimezone(UTC).astimezone(ZoneInfo(zone))
if back.replace(tzinfo=None) != naive: raise ValueError
shift_hours: (end.astimezone(UTC) - start.astimezone(UTC)).total_seconds() / 3600
is_overdue:  check both have tzinfo, then return now > due
```
