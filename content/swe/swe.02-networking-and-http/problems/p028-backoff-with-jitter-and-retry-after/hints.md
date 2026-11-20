## Hint 1

For retry number `i` the **ceiling** is `base * 2**i`, but never more than `cap`. What does the random number do with that ceiling?

## Hint 2

`retry_after`: first decide which form it is: only digits, or a date. A date can be parsed with `email.utils.parsedate_to_datetime`; it raises `ValueError` (or `TypeError`) for garbage.

## Hint 3

```text
delays: [rng.uniform(0, min(cap, base * 2**i)) for i in range(attempts)]
retry_after: None -> None; digits -> int; else parse date -> max(0, (when - now).total_seconds()) or None on error
             then min(result, cap) if cap is given
```
