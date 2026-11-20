## Hint 1

Keep one small table per limiter and update it after every request. Fixed window: which slot is the clock in (`int(t // 10)`) and what is the count in that slot? Sliding log: which times are still in the list after removing those `<= t - 10`? Token bucket: how many tokens now?

## Hint 2

Fixed window: `t=9.9` is slot 0 and slot 0 already counted 5 requests (0, 2, 4, 9, 9.5). At `t=10.1` the slot is 1: the count starts again at 0. Sliding log: at `t=10.1` only the time `0.0` is old enough (`0.0 <= 0.1`) to leave. Token bucket: add `(t - last) * 0.5` tokens, cap at 5, then subtract 1 if you have at least 1.

## Hint 3

```text
bucket tokens before -> after refill -> decision
t=0.0   5.0 -> 5.0  -> yes, 4.0 left
t=2.0   4.0 + 1.0 = 5.0 (cap)  -> yes, 4.0
t=4.0   same as t=2.0
t=9.0   4.0 + 2.5 -> cap 5.0   -> yes, 4.0
t=9.5   4.0 + 0.25 = 4.25      -> yes, 3.25
t=9.9   + 0.2 = 3.45           -> yes, 2.45
... continue; the one "no" appears when tokens fall below 1.0
```
