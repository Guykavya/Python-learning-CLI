## Approach

Keep two variables while reading: `first` (the largest value so far) and `second` (the largest value that is
strictly smaller than `first`). A flag `has_second` says whether `second` exists yet; this is safer than picking
a "very small" starting number, which could clash with real input.

For each new number `x` there are three cases:

- `x > first`: a new maximum. The old maximum is now the second largest distinct value.
- `x == first`: a duplicate of the maximum. Nothing changes; this is what makes `5 5 3` give 3.
- `x < first`: `x` becomes the new `second` if there was no second yet or `x` beats it.

## Trace

Numbers `3 1 8 8 5` (n = 5):

| x | case | first after | second after | has_second |
|---|---|---|---|---|
| 3 (first read) | start | 3 | 0 (unused) | False |
| 1 | x < first, no second yet | 3 | 1 | True |
| 8 | x > first | 8 | 3 | True |
| 8 | x == first | 8 | 3 | True |
| 5 | x < first, 5 > 3 | 8 | 5 | True |

Printed: `5`.

## Code

```python
n = int(input())

first = int(input())
second = 0
has_second = False

for _ in range(n - 1):
    x = int(input())
    if x > first:
        second = first
        has_second = True
        first = x
    elif x < first and (not has_second or x > second):
        second = x
        has_second = True

if has_second:
    print(second)
else:
    print("none")
```

## Complexity

Each number is looked at once with a constant amount of work: O(n) time. Only three variables are kept: O(1) space.

## Another way

**Two passes.** If you could read the data twice (for example from a file, or once you know lists), first find
the maximum, then in a second pass find the largest value that is `< maximum`. That is easier to get right, but
it needs the data twice. With lists you could also sort and walk down from the end until the value changes,
which costs O(n log n). The one-pass method is the one to use on a stream that you can read only once.

## Edge cases

- `n = 1`: the loop never runs, `has_second` stays False, print `none`.
- All values equal: every `x` is `== first`, so `none`.
- Maximum first (`9 2 7`) or last (`3 1 8`): both handled by the two branches.
