## Approach

**List comprehension `a`.** All three `double` calls run at once, so `double 1`, `double 2`,
`double 3` come before `built a`. The loop afterwards only reads the stored values.

**Generator expression `b`.** Creating it runs nothing, so `built b` comes first. The `for` loop
then asks for one value at a time, and each `double` call runs just before its `got` line. The
lines interleave. After the loop, `b` is used up, so `list(b)` is `[]`.

**Generator expression `c`.** Python evaluates the outermost iterable, `source()`, at once when
the generator expression is created. So `source called` comes **before** `built c`. The `x + 1`
part waits until `next(c)`, which gives 11.

## Output

```text
double 1
double 2
double 3
built a
got 2
got 4
got 6
built b
double 1
got 2
double 2
got 4
double 3
got 6
again []
source called
built c
11
```

## Complexity

O(n) work in both cases. The difference is *when* it is done and how much memory is held:
the list keeps all values, the generator keeps one at a time.

## Another way

Wrap the right-hand side in a function call that prints, as `source()` does here, whenever you
are unsure *when* something runs. Print-tracing is the quickest way to see lazy evaluation.
