# Count even and odd numbers

Read a count `c`, then `c` integers, one per line. Print how many of them are even and how many are odd.

- Zero is even (it divides by 2 with nothing left over).
- Negative numbers count too: `-4` is even, `-3` is odd.

## Input

- The first line holds `c`, the number of integers that follow.
- Then `c` lines, each with one integer.

## Output

Exactly two lines:

```
even E
odd O
```

where `E` is the number of even integers and `O` the number of odd ones. Lowercase words, one space before the count.

## Examples

Input:

```
5
1
2
3
4
0
```

Output:

```
even 3
odd 2
```

Input (negative numbers):

```
3
-3
-4
-7
```

Output:

```
even 1
odd 2
```

Input (no numbers at all):

```
0
```

Output:

```
even 0
odd 0
```

## Constraints

- `0 <= c <= 1000`
- Each integer is between `-10^9` and `10^9`.

Use `input()` without a prompt message.

## Before you code

What is `-3 % 2` in Python? Work it out (or recall the floor-division rule) before you choose your test for "odd".
Write your plan as comments at the top of `solution.py`.
