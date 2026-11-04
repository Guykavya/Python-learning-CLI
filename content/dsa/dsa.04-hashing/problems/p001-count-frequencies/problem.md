# Count how often each value appears

A **frequency table** maps each value to the number of times it occurs. A dictionary is the natural tool: the value is
the key, the count is the stored value. Read `n` integers and print one line `value count` for every **distinct**
value, in the order the values **first appeared**.

## Input

- Line 1: `n`.
- Line 2: `n` integers (an empty line when `n = 0`).

## Output

One line per distinct value: `value count`. Nothing is printed when `n = 0`.

## Example

Input:

```
7
3 1 3 2 1 3 5
```

Output:

```
3 3
1 2
2 1
5 1
```

`3` came first and appears three times; `1` came second and appears twice, and so on.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Use `input()` without a prompt message. A dictionary remembers insertion order, so you do not need to sort.
