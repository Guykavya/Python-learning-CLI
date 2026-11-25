## Approach

- F1: `B5` is empty, 1/0: `#DIV/0!`.
- F2: "z" is not in `A1:A4`: `#N/A`.
- F3: IFERROR catches it and returns 0: `0`.
- F4: the error is `#DIV/0!`, not `#N/A`, so IFNA does not catch it: `#DIV/0!`.
- F5: SUM over a range that contains an error returns that error: `#N/A`.

## Code

```text
#DIV/0!
#N/A
0
#DIV/0!
#N/A
```

## Complexity

Not applicable (a trace problem).

## Another way

Use `IFERROR` only where a missing value is genuinely 0 (and say so in a note); otherwise let the error show, or use `IFNA(XLOOKUP(...), "not found")` so that other errors stay visible.
