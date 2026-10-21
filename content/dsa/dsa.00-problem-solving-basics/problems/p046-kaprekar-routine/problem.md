# Kaprekar's routine

Take any 4-digit number whose digits are not all the same. Repeat this step:

1. Arrange its 4 digits in decreasing order to get the **big** number.
2. Arrange them in increasing order to get the **small** number. Zeros go at the front, so `small` can have leading
   zeros (the digits of `2111` give small `1112`, the digits of `0999` give big `9990` and small `0999`).
3. Subtract: `diff = big - small`. Use `diff` (as a 4-digit number, with leading zeros if needed) as the next number.

Surprisingly, you always reach **6174** within at most 7 steps. Once there, you would stay there forever,
because `7641 - 1467 = 6174`.

Read a number and print every step until `diff` is 6174, then the number of steps.

**Rule:** no lists, no `sorted()`, no `str()`. Work with digits using `%` and `//`.

## Input

One line with a 4-digit integer `x`.

## Output

- If all four digits of `x` are the same (like `5555`), print only `invalid`.
- Otherwise, print one line per step, formatted exactly as `f"{big:04d} - {small:04d} = {diff:04d}"`
  (each number padded to 4 digits with leading zeros, with ` - ` and ` = ` between them).
  Stop after the step whose `diff` is `6174`.
- Then print `steps K`, where `K` is the number of steps printed.

If the input is already `6174`, still do one step: print `7641 - 1467 = 6174` and `steps 1`.

## Examples

Input `3524`:

```
5432 - 2345 = 3087
8730 - 0378 = 8352
8532 - 2358 = 6174
steps 3
```

Input `2111`:

```
2111 - 1112 = 0999
9990 - 0999 = 8991
9981 - 1899 = 8082
8820 - 0288 = 8532
8532 - 2358 = 6174
steps 5
```

Input `5555`:

```
invalid
```

## Constraints

- `1000 <= x <= 9999`
- Use `input()` without a prompt message.

## Before you code

The hard part is building `big` and `small` without a list to sort. Here is the idea to plan around:
**count** how many times each digit appears. For digit `d = 9, 8, ..., 0`, look at the 4 digits of the number
(with `% 10` and `// 10`, exactly 4 times, so zeros at the front are counted too) and count the matches.
Then use digit `d` that many times. Work this out by hand for `3087`, then write your plan as comments at the top of
`solution.py`.
