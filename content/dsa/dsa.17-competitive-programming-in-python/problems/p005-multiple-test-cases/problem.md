# Multiple test cases

Many contest problems begin with `t`, the number of test cases, followed by `t` descriptions.

Each test case is: an integer `n`, then `n` integers (`-10**9 <= x <= 10**9`). For each test case print how many of the numbers are **strictly greater than the average** of the `n` numbers.

Do not use floating point: `x` is greater than the average exactly when `x * n > sum`.

## Input

```text
t
n
a_1 ... a_n
n
...
```

Be careful: the `n` numbers of a test case may be spread over **several lines**, and there may be **blank lines** between test cases. Read by tokens, not by lines. `1 <= t <= 10**5`, `1 <= n`, and the total of all `n` is at most `2 * 10**5`.

## Output

One line per test case.

## Example

```text
2
3
1 2 6
4
5 5 5 5
```
```text
1
0
```

In the first case the sum is 9 and `n = 3`: `6 * 3 = 18 > 9` counts, `2 * 3 = 6 < 9` does not, so the answer is 1. In the second case nothing is above the average.
