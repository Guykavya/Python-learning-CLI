## Hint 1

For one bar, the water level is decided by the **lower** of the two highest walls around it. Can you compute
"highest bar from the start up to `i`" for every `i` in one pass? And "highest from `i` to the end" in another?

## Hint 2

With two arrays `left_max` and `right_max`, the answer is `sum(min(left_max[i], right_max[i]) - h[i])`. To drop the
arrays, use two pointers `i` (from the left) and `j` (from the right) with running maxima `left_max` and `right_max`.
If `left_max <= right_max`, which wall limits bar `i`? Do you need to know the exact highest wall on its right?

## Hint 3

```
i = 0, j = n - 1, left_max = right_max = 0, total = 0
while i <= j:
    if left_max <= right_max:
        left_max = max(left_max, h[i]); total += left_max - h[i]; i += 1
    else:
        right_max = max(right_max, h[j]); total += right_max - h[j]; j -= 1
```

Bar `i` is safe to settle because somewhere on its right there is already a wall of height `right_max >= left_max`.
