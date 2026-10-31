**1. What goes wrong.** A naive local string throws away the offset. On 27 October 2024 the
hour 01:00-02:00 happens twice in London: first in BST (UTC+1), then again in GMT (UTC+0). An
entry stored as `"2024-10-27 01:30"` could be either of two instants an hour apart, and nothing in
the row says which. `ORDER BY time` can put a later event before an earlier one (01:45 BST is
before 01:15 GMT in reality), and "who was in the building between 01:00 and 02:00?" mixes two
different hours. A night-shift duration 22:00 -> 06:00 is computed as 8 hours although 9 hours
passed. On 31 March 2024 the opposite happens: 01:00-02:00 does not exist, so a row saying
`01:30` is impossible (a bug or a bad clock), and the 22:00 -> 06:00 shift is really 7 hours, not 8.

**2. Why naive datetimes make it worse.** A naive value has no zone, so Python guesses.
`naive.astimezone(...)` assumes the *computer's* local zone: the result is right on a laptop in
London and wrong on a server in UTC, with no error. Comparing naive with aware raises
`TypeError`, and the "quick fix" of stripping `tzinfo` silently compares wall clocks from
different zones. Even aware values in the *same* zone are subtracted wall clock minus wall clock.

**3. Convert at the edges.** At input, turn every time into an aware UTC value immediately:
`datetime.now(timezone.utc)` for "now", or `local.replace(tzinfo=ZoneInfo("Europe/London")).astimezone(timezone.utc)`
for a time a user typed (and reject times in the gap). Store it as an ISO string with the offset,
`"2024-10-27T00:30:00+00:00"`, or as a Unix timestamp. All sorting, comparing and subtracting
happens in UTC, where every hour exists exactly once. At output, convert with
`.astimezone(ZoneInfo(user_zone))` just before formatting for a human. The same data then works
for users in Kolkata or New York with no change.

**4. When UTC is not enough.** For a **future** event fixed to local time ("dentist at 09:00 on
14 May next year, London"), the UTC instant depends on DST rules that may change before then. If
you stored only the UTC value computed with today's rules, and the rules change, the appointment
would show as 08:00 or 10:00. Store the **wall time and the zone name** (`"2026-05-14 09:00"`,
`"Europe/London"`) and compute the UTC instant when needed, with the tz database current at that
time. Past events (logs, entries, payments) are facts: UTC is right for them.
