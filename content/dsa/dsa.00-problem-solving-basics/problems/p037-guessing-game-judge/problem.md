# Judge a guessing game

A player is trying to guess a secret number between 1 and 100. Your program is the judge.

The first line of input is the secret number. Every line after that is one guess (a whole number).
For each guess, in order, print one line:

- If the guess is less than 1 or greater than 100, print `out of range`. This guess does **not** count.
- If the guess is smaller than the secret, print `higher` (the player should guess higher).
- If the guess is bigger than the secret, print `lower`.
- If the guess equals the secret, print `correct in K guesses`, where `K` is the number of guesses that
  counted, including this one. Then **stop**: do not read or judge any more lines.

The input always contains the correct guess somewhere. There may be more lines after it; ignore them.

## Input

- Line 1: the secret number.
- Lines 2 onward: one guess per line.

## Output

One line per judged guess, using exactly the words above in lowercase. Always write `guesses`
(plural), even when `K` is 1.

## Examples

Input:

```
42
50
0
25
42
```

Output:

```
lower
out of range
higher
correct in 3 guesses
```

The guess `0` is out of range and does not count, so `42` is the 3rd counted guess.

Input (correct at once, with extra lines after it that must be ignored):

```
7
7
100
3
```

Output:

```
correct in 1 guesses
```

## Constraints

- The secret is between 1 and 100.
- Guesses are whole numbers, possibly negative or larger than 100.
- At most 1000 guesses.
- Use `input()` without a prompt message.

## Before you code

You do not know how many guesses there will be, so a `for` loop over a count will not work.
Decide: what kind of loop, what stops it, and when exactly the counter goes up. Write that plan as
comments at the top of `solution.py`, then run the first example through it by hand.
