# Running average until zero

Read whole numbers, one per line, until you read a line containing `0`. The `0` is a **stop signal**,
not data: it is not part of the average and is not counted.

After reading each data number, print the average of all data numbers read so far, with exactly two
digits after the decimal point. When the `0` arrives, print `count C`, where `C` is how many data numbers there were.

If the very first line is `0`, there is no data: print only `count 0`.

## Input

Several lines, one whole number per line. The last line is `0`, and `0` appears nowhere else.
Use `input()` without a prompt message.

## Output

One line per data number with the running average, formatted like `f"{avg:.2f}"` (for example `2.50`, `-1.00`,
`3.33`). Then one final line `count C`.

## Examples

Input:

```
4
1
7
0
```

Output:

```
4.00
2.50
4.00
count 3
```

(4 / 1 = 4.00, then (4 + 1) / 2 = 2.50, then (4 + 1 + 7) / 3 = 4.00.)

Input:

```
-3
2
0
```

Output:

```
-3.00
-0.50
count 2
```

Input:

```
0
```

Output:

```
count 0
```

## Constraints

- Between 0 and 100000 data numbers, each between `-1000000` and `1000000`, never `0`.
- The input always ends with a line `0`.

## Before you code

You do not know in advance how many numbers will come. Which kind of loop fits that: `for` or `while`?
Which two values must you remember to compute the average without storing every number?
Write your plan as comments at the top of `solution.py`.
