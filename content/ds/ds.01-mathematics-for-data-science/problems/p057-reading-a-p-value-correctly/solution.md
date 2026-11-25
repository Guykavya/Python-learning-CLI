## Approach

Two of the 70 splits (all large numbers in one group, either group) reach the observed difference of 4.0: `2/70 = 0.029`.

## Answer

```text
observed difference 4.0
2 of 70 splits are at least this extreme
p = 0.029
reject at 0.05: True
reject at 0.01: False
3 against 3: smallest possible p = 0.100
```

## Another way

p is `P(data this extreme | no real difference)`, not `P(no real difference | data)`; the second needs a prior (Bayes).
