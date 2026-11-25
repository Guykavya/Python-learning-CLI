# Funnel by hand

Chapter section 3.3. Twelve sessions went through four steps: each tuple is `(view, cart, checkout, buy)`, 1 for "reached this step".

```python
sessions = [
    (1, 1, 1, 1), (1, 1, 1, 0), (1, 1, 0, 0), (1, 1, 0, 0),
    (1, 0, 0, 0), (1, 0, 0, 0), (1, 0, 0, 0), (0, 0, 0, 0),
    (1, 1, 1, 1), (1, 1, 1, 0), (0, 0, 0, 0), (1, 1, 0, 0),
]
names = ["view", "cart", "checkout", "buy"]
n = len(sessions)
prev = n
for i, name in enumerate(names):
    k = sum(s[i] for s in sessions)
    print(f"{name:<9}{k:>3} {k / prev * 100:5.1f} {k / n * 100:5.1f}")
    prev = k
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. The format `{name:<9}` pads the name to 9 characters on the right, `{k:>3}` right-aligns the count in 3 characters,
`{...:5.1f}` right-aligns a number with one decimal in 5 characters. Do not run the code before you have written your answer.

## Example

If 5 of 8 sessions viewed, the first line would be `view       5  62.5  62.5`.

## After you answer

- Which step loses the most sessions in absolute numbers, and which loses the largest share of the sessions that reached it?
- Are these the same step?
