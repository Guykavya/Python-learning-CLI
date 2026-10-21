## Approach

**Building big and small without sorting.** We cannot sort a list, but we can **count**. For each digit `d` from 9
down to 0, look at the 4 digits of `x` (take `m % 10`, then `m //= 10`, exactly 4 times) and count how many equal `d`.
Then use `d` that many times. Because `d` goes from 9 down to 0, the digits come out in decreasing order:

- `big = big * 10 + d` appends `d` on the right, so `big` gets the digits in decreasing order.
- `small = small + d * place`, with `place = 1, 10, 100, 1000`, puts each new digit to the **left** of the previous
  ones. The same decreasing sequence then reads in increasing order. Zeros come last, so they land in the highest
  places, which are the leading zeros: `small` for `3087` is `378`, printed as `0378` by `:04d`.

Looking at exactly 4 digits (not `while m > 0`) matters: `999` must be treated as `0999`, with one zero.

**The loop.** The input `6174` must still do one step, so the check `diff == 6174` comes **after** the step
(a loop with `while True:` and `break` at the end). **Invalid input:** the numbers with four equal digits are exactly
the multiples of 1111 (1111, 2222, ..., 9999), so `x % 1111 == 0` detects them.

## Trace

Building big and small for `x = 3087` (digits 3, 0, 8, 7):

| `d` | `count` | `big` after | `small` after | `place` after |
|---|---|---|---|---|
| 9 | 0 | 0 | 0 | 1 |
| 8 | 1 | 8 | 8 | 10 |
| 7 | 1 | 87 | 78 | 100 |
| 6, 5, 4 | 0 | 87 | 78 | 100 |
| 3 | 1 | 873 | 378 | 1000 |
| 2, 1 | 0 | 873 | 378 | 1000 |
| 0 | 1 | 8730 | 378 | 10000 |

`diff = 8730 - 378 = 8352`, printed as `8730 - 0378 = 8352`.

## Code

```python
x = int(input())
if x % 1111 == 0:
    print("invalid")
else:
    steps = 0
    while True:
        big = 0
        small = 0
        place = 1
        for d in range(9, -1, -1):
            # How many times does digit d appear among the 4 digits of x?
            count = 0
            m = x
            for k in range(4):
                if m % 10 == d:
                    count += 1
                m //= 10
            # Use digit d that many times.
            for k in range(count):
                big = big * 10 + d          # add d on the right of big
                small = small + d * place   # add d on the left of small
                place *= 10
        diff = big - small
        steps += 1
        print(f"{big:04d} - {small:04d} = {diff:04d}")
        x = diff
        if diff == 6174:
            break
    print(f"steps {steps}")
```

## Complexity

Each step does 10 digits times 4 checks, about 40 operations, and there are at most 7 steps. That is constant work: O(1).
For numbers with `k` digits, the counting idea costs O(10 * k) per step.

## Another way

Extract the 4 digits into four variables `d1, d2, d3, d4` and sort them with a fixed set of compare-and-swap steps
(a "sorting network": swap if `d1 > d2`, `d3 > d4`, `d1 > d3`, `d2 > d4`, `d2 > d3`). That is fast but fiddly and only
works for exactly 4 digits. Counting (this is the idea behind **counting sort**) works for any number of digits and
is how you sort small whole numbers very quickly. With lists, you would simply use `sorted`.

## Edge cases

- `6174`: one step, `7641 - 1467 = 6174`, `steps 1`.
- `2111`, `1000`, `9998`: the first `diff` is `999`, which must be treated as `0999` in the next step.
- `5555`: `invalid` and nothing else.
