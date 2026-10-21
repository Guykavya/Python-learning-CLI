# Merge two sorted lines

Read two lines of whole numbers. Each line should be sorted from smallest to largest
(repeats allowed).

- If line 1 is not sorted, print `Line 1 is not sorted` and stop. Then the same check for line 2.
- Otherwise print all the numbers from both lines on one line, sorted, separated by spaces.
  Then print `From line 1: A, from line 2: B` (how many numbers came from each).
- If both lines are empty, print `(empty)` instead of the numbers line.

Do **not** use `sorted()` or `.sort()`. Merge the lines by walking through both at once:
always take the smaller front number. When the front numbers are equal, take the one from
line 1 first.

**Example**

Input:
```
1 4 9
2 4 10 11
```
Output:
```
1 2 4 4 9 10 11
From line 1: 3, from line 2: 4
```
