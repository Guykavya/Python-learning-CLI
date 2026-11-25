# Pick a metric from the cost

Chapter section 12. The right metric depends on **what each kind of mistake costs** and on how rare the positive class is. A small decision rule:

```python
def pick(cost_fp, cost_fn, positive_rate, ranking_only):
    if ranking_only:
        return "AUC"
    if positive_rate < 0.05:
        return "recall" if cost_fn > cost_fp else "precision"
    if cost_fp == cost_fn:
        return "accuracy"
    return "precision" if cost_fp > cost_fn else "recall"


stories = [
    ("credit card fraud", 1, 100, 0.01, False),
    ("spam filter", 50, 1, 0.30, False),
    ("interview shortlist", 5, 5, 0.20, True),
    ("quality check", 5, 5, 0.50, False),
    ("rare disease screening", 5, 50, 0.02, False),
    ("production line stop alarm", 500, 20, 0.01, False),
]
for name, cost_fp, cost_fn, rate, ranking in stories:
    print(f"{name}: {pick(cost_fp, cost_fn, rate, ranking)}")
```

(Each story is `(name, cost of a false positive, cost of a false negative, share of positives, ranking only?)`.)

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `("coin toss game", 1, 1, 0.5, False)` the program would print `coin toss game: accuracy`.

## After you answer

- In "production line stop alarm" a false alarm costs 500 and a miss costs 20. Explain in a sentence why the rule says `precision`.
