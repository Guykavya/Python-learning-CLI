# Build a multi-key sorter

Build a small **spreadsheet sort**: records have a `name` (a word), an `age` (integer) and a `score` (integer). You are given a list of **sort rules**, in order of priority
(the first rule is the most important). Each rule is a field and a direction `asc` or `desc`. Sort the records by the rules; records equal under all rules must stay in **input order** (stable).

You must **write the sorting yourself**: a stable merge sort whose comparison follows the rules. `sorted()`, `.sort()`, `heapq`, `bisect` and `cmp_to_key` are not allowed;
the tests read your source.

## Input

- Line 1: `n`.
- Next `n` lines: `name age score`.
- Next line: `k`, the number of rules (may be 0).
- Next `k` lines: `field direction` where `field` is `name`, `age` or `score` and `direction` is `asc` or `desc`.

## Output

`n` lines `name age score` in sorted order. Names compare as strings (alphabetically), ages and scores as integers.

## Example idea

Rules `age desc`, `name asc`: oldest first, and among people of the same age, names A to Z. With **no** rules the output equals the input.

## Constraints

- `1 <= n <= 50000`
- `0 <= k <= 6`, a field may appear more than once (later duplicates never matter)
- `0 <= age, score <= 10^9`, names have 1 to 10 lowercase letters

## Example

Input:

```
5
ann 30 80
bob 25 90
cy 30 70
dee 25 90
eli 35 60
2
age desc
name asc
```

Output:

```
eli 35 60
ann 30 80
cy 30 70
bob 25 90
dee 25 90
```
