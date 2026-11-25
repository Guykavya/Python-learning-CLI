## Hint 1

Take the jobs one by one. For each of `created_at` and `started_at` ask: is it `>= 1 Feb` **and** `< 1 Mar`? A missing
`started_at` is never in the month. Then `T` uses the created time, and `C` and `P` use the start time together with the
status. After that, a job in only one of `T` and `C` takes its reason from the matching function.

## Hint 2

```text
201: created Feb 03 (T), completed, started Feb 04 (C)  -> T,C
202: T; cancelled, never started                         -> T cancelled (never started)
203: created Jan 31 23:59:59 (not T), started Feb 01 00:00:00 (in), completed -> C created in January, started in February
204: T; completed, started Mar 01 00:00:00 (end excluded: not C) -> T started in March or later
205: T; pending, started NaT                              -> T pending (no start date yet)
206: T; failed                                            -> T failed
207: not T (created in January), pending and started Feb 09 -> P (no reason)
lists: T = [201, 202, 204, 205, 206], C = [201, 203];  sizes: 5, 2, 1, and 1 in both
last line: jobs only in T (4) minus jobs only in C (1)
```
