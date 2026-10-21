# Is it on the list?

A library has a list of `n` registered member numbers. Then `q` people arrive, each giving a number.
For each person print `YES` if their number is registered, otherwise `NO`.

`starter.py` is correct but uses `x in members` with a list. With 100000 members and 100000 visitors it takes
close to a minute. Make it fast.

## Input

- Line 1: `n`.
- Line 2: `n` member numbers separated by spaces.
- Line 3: `q`.
- Then `q` lines, each with one number.

## Output

`q` lines, each `YES` or `NO`.

## Example

Input:

```
4
17 3 42 8
3
42
5
17
```

Output:

```
YES
NO
YES
```

## Constraints

- `1 <= n, q <= 100000`
- member numbers and queries are between `1` and `10^9`; member numbers may repeat

Use `input()` without a prompt message.
