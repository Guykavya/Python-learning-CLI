## Approach

Trace each limiter on its own, then read across the lines.

```text
t=0.0 fixed=yes sliding=yes bucket=yes
t=2.0 fixed=yes sliding=yes bucket=yes
t=4.0 fixed=yes sliding=yes bucket=yes
t=9.0 fixed=yes sliding=yes bucket=yes
t=9.5 fixed=yes sliding=yes bucket=yes
t=9.9 fixed=no sliding=no bucket=yes
t=10.1 fixed=yes sliding=yes bucket=yes
t=10.2 fixed=yes sliding=no bucket=yes
t=10.5 fixed=yes sliding=no bucket=no
t=12.0 fixed=yes sliding=yes bucket=yes
t=14.0 fixed=yes sliding=yes bucket=yes
allowed: fixed=10 sliding=8 bucket=10
```

**Fixed window.** Slot 0 (seconds 0 to 10) counts requests at 0, 2, 4, 9 and 9.5: five, so the 9.9 request is refused. At 10.1 the slot becomes 1 and the counter restarts at 0, so the next five (10.1, 10.2, 10.5, 12, 14) all pass. The `yes` answers at 9.0, 9.5, 10.1, 10.2, 10.5, 12.0 and 14.0 all fall inside one 10-second span (after 4.0, up to 14.0): **seven** requests, more than "5 per 10 s". This is the boundary burst of the chapter.

**Sliding log.** The list after the first five is `[0, 2, 4, 9, 9.5]`. At 9.9 nothing is old enough to leave (`0 <= -0.1` is false), so refused. At 10.1 the entry `0` leaves (`0 <= 0.1`), one slot is free, allowed: `[2, 4, 9, 9.5, 10.1]`. At 10.2 and 10.5 `2` has not left yet (`2 <= 0.2` and `2 <= 0.5` are false): refused. At 12 the entry `2` leaves (`2 <= 2`, the boundary is *inclusive*): allowed. At 14 the entry `4` leaves: allowed. Any 10-second period has at most 5 allowed requests.

**Token bucket** (tokens after the decision):

```text
t     tokens before   refill        after refill   decision   after
0.0   5               -             5              yes        4
2.0   4               +1.0          5 (cap)        yes        4
4.0   4               +1.0          5 (cap)        yes        4
9.0   4               +2.5          5 (cap)        yes        4
9.5   4               +0.25         4.25           yes        3.25
9.9   3.25            +0.2          3.45           yes        2.45
10.1  2.45            +0.1          2.55           yes        1.55
10.2  1.55            +0.05         1.6            yes        0.6
10.5  0.6             +0.15         0.75           NO         0.75
12.0  0.75            +0.75         1.5            yes        0.5
14.0  0.5             +1.0          1.5            yes        0.5
```

The bucket allows a burst of up to `capacity`, then only the refill rate. Because it was full at 9.0, it let eight requests through between 9.0 and 10.2 (the burst, plus a little refill): that is by design, not a bug. Its promise is "never more than `capacity + rate * period`", here `5 + 0.5 * 10 = 10` in any 10 seconds.

The output was obtained by working out the three tables above by hand and then running the program with Python 3.14 (it uses only the standard library); both agreed. The totals line is `fixed=10 sliding=8 bucket=10`.

## Complexity

Each request costs O(1) for the fixed window and the bucket, and O(limit) memory for the sliding log (one entry per recent request).

## Another way

A good rule to check yourself: the sliding log must never show more than 5 `yes` in any span of 10 seconds. Take the span after 4.0 up to 14.0: sliding has 9.0, 9.5, 10.1, 12.0, 14.0 (five, as promised); fixed has seven; the bucket also has seven (9.0, 9.5, 9.9, 10.1, 10.2, 12.0, 14.0), which is allowed for a bucket because its promise is `capacity + rate * period` = 10.

## After you answer: model answers

1. In the span after `t=4.0` up to `t=14.0`: fixed window 7 `yes`, sliding log 5, token bucket 7. The fixed window breaks the idea of a 10-second limit the most: its worst case is 10 requests in 0.2 seconds (chapter 11.2), because the counter resets at the clock edge, whatever time the client really sent. The bucket's 7 is inside its own promise (up to 10 per 10 s); the sliding log is the only one that is exact.
2. `capacity` is the largest burst; `rate` is the long-run average. A bucket with capacity 5 and rate 0.5 per second is *not* the same as "exactly 5 per 10 seconds": it allows a burst of 5 plus whatever refilled meanwhile.
3. Login: a token bucket per `(username, IP)` with a small capacity, or a sliding log if you need an exact count. Public read API: a token bucket with a bigger capacity, because page loads come in bursts.
