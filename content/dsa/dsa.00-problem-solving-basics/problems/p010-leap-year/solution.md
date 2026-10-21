## Approach

Write the rule as a chain of checks from the most specific to the most general. A year divisible by 400
is also divisible by 100 and by 4, so the 400 test must come first; otherwise the 100 test would catch 2000
and reject it.

## Trace

There is no loop here, so trace the chain of checks for each example year.

| `year` | `% 400 == 0` | `% 100 == 0` | `% 4 == 0` | Output |
|---|---|---|---|---|
| 2000 | True | (not checked) | (not checked) | `leap` |
| 1900 | False | True | (not checked) | `not leap` |
| 2024 | False | False | True | `leap` |
| 2023 | False | False | False | `not leap` |

## Code

```python
year = int(input())
if year % 400 == 0:
    print("leap")
elif year % 100 == 0:
    print("not leap")
elif year % 4 == 0:
    print("leap")
else:
    print("not leap")
```

## Complexity

A fixed number of checks: O(1).

## Another way

One boolean expression:

```python
year = int(input())
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    print("leap")
else:
    print("not leap")
```

Read it as "divisible by 4 but not by 100, or divisible by 400". It is shorter, but the parentheses and the
`!=` are easy to get wrong. The `if / elif` chain is easier to check line by line against the rule, so prefer
it while you are learning, or whenever the rules have several layers of exceptions.

## Edge cases

- `1600` and `2000`: divisible by 400, so leap.
- `1900` and `2100`: divisible by 100 but not 400, so not leap.
- `4` is leap; `1` is not.
