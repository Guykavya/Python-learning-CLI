## Approach

Loop `i` from 1 to `n`. For each `i`, exactly one of four things is printed, so use a single
`if / elif / elif / else` chain. The most specific case, "divisible by both", must come first; otherwise the
"divisible by `a`" branch would catch those numbers and print `Fizz`.

Note that "divisible by both `a` and `b`" is not the same as "divisible by `a * b`". With `a = 2` and `b = 2`,
the number 2 is divisible by both, but not by 4. Testing each divisor separately with `and` is always correct.

## Trace

Input `a = 2`, `b = 3`, `n = 6`.

| Iteration | `i` | `i % a` | `i % b` | Printed |
|---|---|---|---|---|
| 1 | 1 | 1 | 1 | `1` |
| 2 | 2 | 0 | 2 | `Fizz` |
| 3 | 3 | 1 | 0 | `Buzz` |
| 4 | 4 | 0 | 1 | `Fizz` |
| 5 | 5 | 1 | 2 | `5` |
| 6 | 6 | 0 | 0 | `FizzBuzz` |

## Code

```python
a = int(input())
b = int(input())
n = int(input())
for i in range(1, n + 1):
    if i % a == 0 and i % b == 0:
        print("FizzBuzz")
    elif i % a == 0:
        print("Fizz")
    elif i % b == 0:
        print("Buzz")
    else:
        print(i)
```

## Complexity

One line per `i`, a fixed number of checks each: O(n).

## Another way

Build the word piece by piece:

```python
for i in range(1, n + 1):
    word = ""
    if i % a == 0:
        word = word + "Fizz"
    if i % b == 0:
        word = word + "Buzz"
    if word == "":
        print(i)
    else:
        print(word)
```

Here the order problem disappears: "both" is simply both pieces glued together. This style scales better if a
third rule is added later (say `Jazz` for multiples of `c`): you add one `if` instead of rewriting a chain of
every combination.

## Edge cases

- `n = 0`: the range is empty and nothing is printed.
- `a == b`: every multiple of `a` is `FizzBuzz`; `Fizz` and `Buzz` never appear alone.
- `a = 1`: every number is at least `Fizz`.
