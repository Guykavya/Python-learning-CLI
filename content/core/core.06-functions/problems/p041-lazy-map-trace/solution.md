## Walkthrough

- Creating `m` calls nothing, so `created` is printed first. `list(m)` then calls `noisy` three
  times (each prints) and shows `[10, 20, 30]`. The second `list(m)` gets `[]`: the iterator is
  used up.
- `sum(evens)` adds 2 + 4 + 6 = 12; the second `sum` of the same, exhausted filter is 0.
- `any` pulls values from `m2` one at a time: 40 (not > 45), then 50 (yes), and stops. So `noisy`
  ran for 4 and 5 only. `list(m2)` then takes the **remaining** values, 6 and 7.
- `map(len, words)` has not read anything when `"dddd"` is appended, so the list it walks later
  has four words: `[1, 2, 3, 4]`. Laziness means the iterator sees the list as it is when the
  values are pulled.

## The exact output

```text
created
  noisy 1
  noisy 2
  noisy 3
[10, 20, 30]
[]
12 0
  noisy 4
  noisy 5
True
  noisy 6
  noisy 7
[60, 70]
[1, 2, 3, 4]
```
