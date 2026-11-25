## Approach

Apply the three masks to each job, then the two reason functions to the jobs that are in exactly one of `T` and `C`.

1. `201`: created and started in February, completed: in `T` and `C`, no reason.
2. `202`: cancelled, created in February: `T` only, reason `cancelled (never started)`.
3. `203`: created at 23:59:59 on 31 January (before the start of the half-open month), started exactly at `1 Feb 00:00`
   (the start is included), completed: `C` only, reason `created in January, started in February`.
4. `204`: created in February, started exactly at `1 Mar 00:00` (the end is excluded), so not in `C`: `T` only,
   reason `started in March or later`.
5. `205`: pending, never started: `T` only, reason `pending (no start date yet)`. It can never be in `P`.
6. `206`: failed: `T` only, reason `failed`.
7. `207`: created in January, pending, started on 9 February: in `P` only, so no reason.
8. `T` has 5 jobs, `C` 2, `P` 1, and 1 job is in both.
9. Only in `T`: 202, 204, 205, 206 (4 jobs). Only in `C`: 203 (1 job). 4 - 1 = 3 is the net gap 5 - 2: four jobs leave and
   one enters.

## Output

```text
201 T,C
202 T cancelled (never started)
203 C created in January, started in February
204 T started in March or later
205 T pending (no start date yet)
206 T failed
207 P
[201, 202, 204, 205, 206]
[201, 203]
5 2 1 1
3
```
