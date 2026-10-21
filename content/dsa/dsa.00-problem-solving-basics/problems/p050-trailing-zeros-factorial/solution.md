## Approach

A trailing zero is a factor 10 = 2 * 5 in `n!`. So the number of zeros is the number of complete
(2, 5) pairs among all the factors of `1 * 2 * ... * n`.

**Why 2s are always plentiful.** Every second number is even and gives at least one 2, while only
every fifth number gives a 5. Among 1..n there are `n // 2` multiples of 2 but only `n // 5`
multiples of 5 (and the same holds for 4 versus 25, 8 versus 125, ...). So there are always at
least as many 2s as 5s, and the number of 5s decides the answer.

**Counting the 5s.** Each multiple of 5 up to `n` gives one 5: that is `n // 5`. Each multiple of
25 gives one *more* 5: add `n // 25`. Each multiple of 125 gives a third: add `n // 125`. Keep going
while the power of 5 is at most `n`.

## Trace

Input `125`:

| power | n // power | count |
|---|---|---|
| 5 | 25 | 25 |
| 25 | 5 | 30 |
| 125 | 1 | 31 |
| 625 | (loop stops: 625 > 125) | 31 |

Output: `31`.

## Code

```python
n = int(input())

# Each trailing zero needs a 2 and a 5. There are always more 2s, so count the 5s.
count = 0
power = 5
while power <= n:
    count += n // power   # numbers up to n that contain this power of 5
    power *= 5
print(count)
```

## Complexity

The power of 5 grows five times each step, so the loop runs about log base 5 of `n` times:
26 steps for `n = 10^18`. That is O(log n) time and O(1) memory.

## Another way

Divide `n` itself instead of growing a power: `while n > 0: n //= 5; count += n`. After the first
division `n` holds `n // 5`, after the second `n // 25`, and so on, so it adds the same terms.
It never builds a number larger than `n`, which matters in languages with fixed-size integers
(where `power *= 5` could overflow). In Python both are fine.

## Edge cases

- `n = 0` and `n < 5`: the loop never runs and the answer is 0, which is correct (0! = 1, 4! = 24).
- `n = 25`, `125`, `625`: each crosses a new power of 5 and adds an extra 5.
