# Fix with regularisation or data?

Chapter section 7. Once a learning curve tells you what is wrong, the remedy depends on whether collecting more data is likely to help. A small decision table:

```python
def action(gap, val_err, floor, still_falling):
    if gap > 0.15 * val_err:
        return "collect more data" if still_falling else "regularise or simplify"
    if val_err > 1.25 * floor:
        return "add capacity or features"
    return "stop: near the noise floor"


summaries = [
    ("S1", 0.85, 0.90, 0.30, True),
    ("S2", 0.50, 0.60, 0.30, False),
    ("S3", 0.03, 0.55, 0.30, False),
    ("S4", 0.02, 0.31, 0.30, False),
]
for name, gap, val_err, floor, falling in summaries:
    print(f"{name}: {action(gap, val_err, floor, falling)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `("S9", 0.40, 0.50, 0.30, True)` the program would print `S9: collect more data` (the gap 0.40 is above 0.15 * 0.50 = 0.075).

## After you answer

- S2 and S1 both have a big gap. Why do they get different advice? What would you look at on the learning curve to set `still_falling`?
