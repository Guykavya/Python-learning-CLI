# Fix the stable merge sort

`starter.py` reads `n` records `key label` and should print them sorted **stably** by `key` ascending (records with equal keys must keep their input order).
It is a merge sort, and it is almost right. It has **three bugs**. Find them and fix them. Do not rewrite it from scratch: each fix is one line.
Do not replace it with `sorted()` or `.sort()`: the tests read your source.

Where to look, without saying what is wrong:

1. Run it on `2` records with the same key. Which label comes first? Which comparison operator decides that?
2. Run it on records `(1,a) (2,b)`: does everything come back? What happens to the values left over when one half is used up?
3. Run it on 3 records. Count what comes out. How are the two halves cut?

## Input

- Line 1: `n`.
- Next `n` lines: `key label` (an integer key and a lowercase word).

## Output

`n` lines `key label` in stable ascending order of `key`.

## Constraints

- `1 <= n <= 100000`

## Example

Input:

```
5
2 ann
1 bob
2 cy
1 dee
3 eli
```

Output:

```
1 bob
1 dee
2 ann
2 cy
3 eli
```
