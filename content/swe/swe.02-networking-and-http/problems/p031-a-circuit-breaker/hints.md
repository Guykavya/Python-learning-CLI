## Hint 1

What does the breaker need to remember? Two things: how many failures in a row, and when it opened (or that it is not open). Can `state` be computed from those two plus the clock, without storing it?

## Hint 2

Compute `state` first at the start of `call`, then decide: `open` means refuse; `closed` and `half-open` both run the function but react differently to a failure.

## Hint 3

```text
state: opened_at is None -> "closed"; clock() - opened_at >= cooldown -> "half-open"; else "open"
call: state == open -> raise CircuitOpen
      try fn: on exception: half-open -> opened_at = now; else failures += 1 and open when >= threshold; re-raise
      on success: failures = 0; opened_at = None; return the result
```
