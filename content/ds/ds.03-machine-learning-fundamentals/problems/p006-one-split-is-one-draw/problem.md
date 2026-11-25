# One split is one draw

Chapter section 4.2. The score you measure on a test set depends on **which rows** ended up in it. Here is a tiny, fully deterministic "split" (it rotates the rows instead of shuffling randomly, so you can trace it by hand) and a fixed rule that was **not** fitted to the data.

```python
data = [(1, 0), (2, 0), (3, 1), (4, 0), (5, 1), (6, 1)]       # (x, label)


def rule(x):
    return 1 if x >= 3 else 0


def split(seed):
    k = 2 * seed
    rotated = data[k:] + data[:k]
    return rotated[:-3], rotated[-3:]          # (train, test)


scores = []
for seed in range(3):
    train, test = split(seed)
    hits = sum(1 for x, label in test if rule(x) == label)
    accuracy = hits / len(test)
    scores.append(accuracy)
    print(f"seed {seed}: test x = {[x for x, _ in test]}, accuracy {accuracy:.3f}")
print(f"range of accuracy: {min(scores):.3f} to {max(scores):.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If `data = [(1, 0), (2, 1)]` and the test set were `[(2, 1)]`, the rule predicts 0 for `x = 2`: `hits` is 0 and the accuracy line would show `0.000`.

## After you answer

- The same rule scores two different accuracies on different test sets. What does this say about trusting one split? What would you do about it?
