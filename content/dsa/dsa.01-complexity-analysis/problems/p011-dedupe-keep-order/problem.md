# Remove repeats, keep the first

Read a list of numbers and print each value once, in the order in which it **first** appeared.

`starter.py` does this with `if x not in result`, where `result` is a list. That is correct, but when most values
are different it becomes O(n^2). Make it fast and keep the same output.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

- Line 1: the number of different values.
- Line 2: the different values in order of first appearance, separated by single spaces.

## Example

Input:

```
8
4 1 4 2 1 1 9 2
```

Output:

```
4
4 1 2 9
```

## Constraints

- `1 <= n <= 200000`
- values are between `-10^9` and `10^9`

Use `input()` without a prompt message.
