# Fix the broken lower bound

`starter.py` was meant to print, for each query `x`, the **lower bound**: the first index `i` with `a[i] >= x`, or `n` if there is none. For example for `[1, 2, 2, 2, 5]` and `x = 2` the answer is `1`, and for `x = 9` it is `5`.
It contains **two** bugs, and it prints wrong numbers for some inputs. Find and fix them. Do not rewrite it with `bisect`: that is not allowed here. Keep the half-open template.

Run the tests; each failing assert names the symptom. Then explain to yourself (and in the comments of your solution) what each bug did.

## Input

- Line 1: `n`. Line 2: `n` integers in non-decreasing order.
- Line 3: `q`. Line 4: `q` integers.

## Output

`q` lines, one number each.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`, `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
5
1 2 2 2 5
3
2 9 0
```

Output:

```
1
5
0
```
