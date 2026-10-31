# Explain: the hidden memory cost of tee

`itertools.tee(it)` gives two iterators that both produce all the items of `it`, even though `it`
can be read only once. Arjun tries it:

```python
from itertools import count, islice, tee

a, b = tee(count())
first_a = list(islice(a, 5))
print(first_a)
print(next(b), next(b))

big_a, big_b = tee(range(10_000_000))
total = sum(big_a)          # big_a runs to the end first
print(total)
print(next(big_b))          # big_b has not moved yet
```

Output:

```text
[0, 1, 2, 3, 4]
0 1
49999995000000
0
```

Then he measures the peak memory of two small programs with `/usr/bin/time -v` (the numbers are
from one Linux laptop; yours will differ):

| Program | Peak memory |
|---|---|
| `big_a, big_b = tee(range(10_000_000))`, then `sum(big_a)`, then `next(big_b)` | about 400 MB |
| `big_a, big_b = tee(range(10_000_000))`, then `sum(x + y for x, y in zip(big_a, big_b))` | about 10 MB |

In `answer.md` (about 150 to 300 words), explain:

1. How can `b` still give `0` and `1` after `a` has already read five items? Where are those items kept?
2. Why does the first big program need about 400 MB, while the second needs about 10 MB, though both use `tee` on the same data?
3. State a rule: when is `tee` cheap, and when is it no better (or worse) than `list()`?
4. What happens to the original iterator `it` after you call `tee(it)`? Why must you stop using it directly?
5. For the first big program, what would you write instead?
