## Walkthrough

- **A, B** Ordinary times. January is winter time in New York (EST, -05:00), July is summer time (EDT, -04:00).
- **C** 02:30 on 10 March 2024 does not exist: the clocks went from 01:59 to 03:00. `zoneinfo`
  does not raise an error. With `fold=0` it uses the offset from *before* the jump: `-05:00`, `EST`.
- **D** Converting fixes the impossible time. 02:30 at -05:00 is 07:30 UTC. The jump happened at
  02:00 EST = 07:00 UTC, so 07:30 UTC is already summer time: 07:30 - 4 h = **03:30 EDT**.
  A round trip through UTC is how you "normalise" a time from the gap.
- **E** `before + timedelta(days=1)` adds one day to the *wall clock*: 9 March 09:00 becomes
  10 March 09:00. The zone is kept and the offset is worked out again: by then it is EDT.
- **F** `later - before`: both have the same `tzinfo` object (`ny`), so Python subtracts the wall
  clocks and ignores the offsets: exactly `1 day, 0:00:00`.
- **G** In UTC: 9 March 09:00 EST is 14:00 UTC; 10 March 09:00 EDT is 13:00 UTC. Only
  **23 hours** really passed, because one hour was skipped. Elapsed time must be computed in UTC.
- **H, I** 01:30 on 3 November 2024 happens twice. `fold=0` is the first one (still EDT, -04:00),
  `fold=1` is the second one (already EST, -05:00).
- **J** Same `tzinfo` object again: the comparison looks only at the wall clocks and ignores
  `fold`. Both say 01:30, so `True`, even though they are an hour apart in reality.
- **K** In UTC the first is 05:30, the second 06:30: `1:00:00`.
- **L, M, N** The fall-back jump is at 02:00 EDT = 06:00 UTC. 05:30 UTC is before it, so it shows
  01:30 EDT. 06:30 UTC is after it, so it shows 01:30 EST, and `astimezone` sets `fold=1` because
  it is the second 01:30.
- **O** London's gap: 01:00 GMT jumps to 02:00 BST on 31 March 2024, so 01:30 does not exist. As
  in `C`, `fold=0` uses the offset before the jump: `+00:00`, `GMT`.
- **P** 01:30 at +00:00 is 01:30 UTC, which is after the 01:00 UTC jump: 01:30 + 1 h = **02:30 BST**.

The lessons: wall-clock arithmetic (`+ timedelta`) is right for "same time tomorrow", UTC
arithmetic is right for "how long did it take"; a time in the gap is silently accepted; and only
`fold` tells the two copies of a repeated time apart.

## The exact output

```text
A 2024-01-15T12:00:00-05:00 EST
B 2024-07-15T12:00:00-04:00 EDT
C 2024-03-10T02:30:00-05:00 EST
D 2024-03-10T03:30:00-04:00 EDT
E 2024-03-10T09:00:00-04:00 EDT
F 1 day, 0:00:00
G 23:00:00
H 2024-11-03T01:30:00-04:00 EDT
I 2024-11-03T01:30:00-05:00 EST
J True
K 1:00:00
L 2024-11-03T01:30:00-04:00 EDT
M 2024-11-03T01:30:00-05:00 EST
N 1
O 2024-03-31T01:30:00+00:00 GMT
P 2024-03-31T02:30:00+01:00 BST
```
