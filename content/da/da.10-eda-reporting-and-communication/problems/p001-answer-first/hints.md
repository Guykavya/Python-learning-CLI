## Hint 1

Round first, then compare: 4.04 and 4.01 both read 4.0, so the honest verb is "stayed at". Which three cases are there, and which part of the sentence is the same in all of them?

## Hint 2

```text
b, a = round(before, 1), round(after, 1)
if a > b: core = f"{metric} rose from {b:.1f}{unit} to {a:.1f}{unit} in {period}"
elif a < b: ... "fell" ...
else: core = f"{metric} stayed at {b:.1f}{unit} in {period}"
if cause: core += f", mainly because {cause}"
check the word count, then return core
```
