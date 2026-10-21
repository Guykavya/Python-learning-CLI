## Approach

Check the lengths, then walk both lines together with `zip`, printing and adding up.

## Code

```python
names = input().split()
scores = input().split()
if len(names) != len(scores):
    print(f"Mismatch: {len(names)} names, {len(scores)} scores")
elif not names:
    print("No data")
else:
    total = 0
    for name, score in zip(names, scores):
        print(f"{name}: {score}")
        total += int(score)
    print(f"Average: {total / len(names):.1f}")
```

## Why check the lengths first

`zip` stops at the shortest input without any warning. With 3 names and 2 scores, it would
quietly drop the third name. `zip(names, scores, strict=True)` would raise an error instead;
here we want a friendly message, so we check ourselves.

## Another way

`total = sum(int(s) for s in scores)` adds the scores in one line.
