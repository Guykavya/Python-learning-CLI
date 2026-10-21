# Palindrome number pyramid

Read `n` and print a pyramid of `n` rows. Row `i` (counting from 1) is:

- `n - i` spaces, then
- the numbers 1, 2, ..., i counting up, followed by i - 1, ..., 2, 1 counting down,
  all written next to each other **without spaces**.

Each number is written as its **last digit only** (`value % 10`), so 10 is written `0`,
11 is written `1`, and so on. No line has trailing spaces.

Every row reads the same forwards and backwards (a palindrome), and the rows line up into a
centred triangle.

## Input

One line: the integer `n`. Use `input()` without a prompt message.

## Output

Exactly `n` lines, as described.

## Examples

Input `3`:

```
  1
 121
12321
```

Input `1`:

```
1
```

Input `11` (the last two rows show the "last digit" rule: 10 becomes `0`, 11 becomes `1`):

```
          1
         121
        12321
       1234321
      123454321
     12345654321
    1234567654321
   123456787654321
  12345678987654321
 1234567890987654321
123456789010987654321
```

## Constraints

- 1 <= n <= 30

## Before you code

Do not try to write it all at once. For row `i = 4` with `n = 5`, write down separately: how many
spaces, which numbers going up, which numbers coming down. Turn each part into its own loop, and
write that plan as comments at the top of `solution.py`.
