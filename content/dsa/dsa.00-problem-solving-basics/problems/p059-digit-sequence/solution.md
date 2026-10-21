## Approach

Plan in three steps.

**1. Find the block.** Numbers with the same number of digits form a block:

| length | numbers | count | digits in block |
|---|---|---|---|
| 1 | 1..9 | 9 | 9 |
| 2 | 10..99 | 90 | 180 |
| 3 | 100..999 | 900 | 2700 |
| d | 10^(d-1) .. 10^d - 1 | 9 * 10^(d-1) | d * 9 * 10^(d-1) |

While `k` is larger than the whole current block, subtract the block's digits and move on. Even for
`k = 10^18` this takes fewer than 20 steps, because the blocks grow ten times each step.

**2. Find the number.** Now `k` is a 1-based position inside a block of numbers that all have `length`
digits, starting at `start`. Positions 1..length belong to `start`, the next `length` to `start + 1`,
and so on. With 0-based counting, `(k - 1) // length` numbers come before ours, so
`number = start + (k - 1) // length`, and `index = (k - 1) % length` is the digit's place from the left.

**3. Extract the digit.** There are `length - 1 - index` digits to its right. Remove them with `// 10`
that many times, then take `% 10`.

## Trace

Input `k = 190`:

| step | k | length | count | start | note |
|---|---|---|---|---|---|
| start | 190 | 1 | 9 | 1 | 190 > 9: skip |
| skip | 181 | 2 | 90 | 10 | 181 > 180: skip |
| skip | 1 | 3 | 900 | 100 | 1 <= 2700: stop |

`number = 100 + 0 // 3 = 100`, `index = 0 % 3 = 0`, `drop = 2`: 100 -> 10 -> 1, and `1 % 10 = 1`.
Output `1`.

## Code

```python
k = int(input())

# Step 1: skip whole blocks of numbers with the same number of digits.
length = 1      # digits per number in the current block
count = 9       # how many numbers have this many digits (9, 90, 900, ...)
start = 1       # the first number in the block (1, 10, 100, ...)
while k > length * count:
    k -= length * count
    length += 1
    count *= 10
    start *= 10

# Step 2: k is now a position inside this block (1-based).
number = start + (k - 1) // length     # which number holds the digit
index = (k - 1) % length               # which digit of it, 0 = leftmost

# Step 3: drop the digits to the right of the one we want, then take the last digit.
drop = length - 1 - index
while drop > 0:
    number //= 10
    drop -= 1
print(number % 10)
```

## Complexity

The block loop runs once per digit length (at most about 17 times for `k = 10^18`), and the drop loop
at most `length` times. That is O(log k) time and O(1) memory.

## Another way

**Count digits up to a number, then binary search.** The number of digits used by 1..x can be computed
with the same block table. You can then search for the smallest `x` whose total reaches `k`. That is
more work here, but the "count up to x, then search" idea solves many harder versions of this problem
(for example when the blocks are not this regular). Brute force (`"".join(...)` with strings) is the
right tool for **checking** small `k`, which is what the tests do.

## Edge cases

- `k = 9`, `189`, `2889`: the last digit of a block. The loop must stop (`k > ...` is false when equal).
- `k = 10`, `190`, `2890`: the first digit of the next block.
- Digits 0 inside numbers like 100: correct only if you drop the right digits before `% 10`.
