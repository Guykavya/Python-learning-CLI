# Largest and smallest

Read a count `n`, then `n` integers, one per line. Print the largest and the smallest of them.

**Rule:** do not store the numbers. No lists, no `sorted()`. Keep track of the answer as the numbers arrive,
one at a time. (Think of numbers being read out to you, and you may only remember two of them.)

## Input

- The first line holds `n`, the number of integers that follow.
- Then `n` lines, each with one integer.

## Output

Exactly two lines:

```
max X
min Y
```

where `X` is the largest number and `Y` the smallest. Lowercase words, one space before the number.

## Examples

Input:

```
4
3
-1
9
2
```

Output:

```
max 9
min -1
```

Input (all negative):

```
3
-5
-2
-8
```

Output:

```
max -2
min -8
```

Input (only one number):

```
1
42
```

Output:

```
max 42
min 42
```

## Constraints

- `1 <= n <= 1000`
- Each integer is between `-10^18` and `10^18`.

Use `input()` without a prompt message.

## Before you code

Your biggest decision is what the "largest so far" starts as. Try starting it at `0` on the all-negative example. What goes wrong?
Write your plan as comments at the top of `solution.py`.
