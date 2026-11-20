# A full contest problem set

A tiny contest in one file. Your program reads **one letter** (`A`, `B` or `C`) on the first line, then the input of that problem, and prints its answer. All three problems must be solved in the same `solution.py`, each with the speed that its limits need.

## Problem A: Deletions

`t` test cases (`1 <= t <= 10**5`). Each is a string `s` of lowercase letters (total length at most `2 * 10**5`). You may delete characters. Print the **minimum number of deletions** so that no two neighbouring characters are equal.

```text
A
2
aabbb
abab
```
```text
3
0
```

(`aabbb` becomes `ab`: delete 3.)

## Problem B: Pairs with sum k

`t` test cases. Each has `n k` on one line and then `n` integers `a_i` (`0 <= a_i <= 10**9`); the total of all `n` is at most `2 * 10**5`. Print the number of pairs `i < j` with `a_i + a_j = k`.

```text
B
1
5 6
1 5 3 3 3
```
```text
4
```

(`(1, 5)` and three pairs of the three 3s.)

## Problem C: Islands

First `n m` (`1 <= n, m <= 1000`), then `n` strings of `.` and `#`. Print the number of **islands**: groups of `#` cells connected by side (up, down, left, right).

```text
C
3 4
##..
#..#
..##
```
```text
2
```

## Time limit

Every test has a time limit; the big ones need fast input, one write for the output, a linear algorithm and no recursion. Messages tell you which problem failed.
