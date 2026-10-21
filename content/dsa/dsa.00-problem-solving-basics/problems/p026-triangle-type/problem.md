# What kind of triangle?

Read three whole numbers `a`, `b`, `c`: the proposed side lengths of a triangle, in **any order**.

First decide whether they can form a real triangle:

- every side must be positive (greater than 0), and
- the largest side must be **strictly smaller** than the sum of the other two.
  If it is equal, the "triangle" is flat (all three corners on one line), and we count that as invalid too.

If the sides are not valid, print `invalid` and nothing else.

Otherwise print two lines:

1. the type by sides: `equilateral` (all three equal), `isosceles` (exactly two equal) or `scalene` (all different);
2. `right` if the triangle has a right angle, otherwise `not right`. A triangle is right-angled exactly when
   (largest side)^2 = (sum of the squares of the other two sides). Remember the largest side can be any of `a`, `b`, `c`.

## Input

Three lines: `a`, `b`, `c`. Use `input()` without a prompt message.

## Output

Either the single line `invalid`, or two lines as described above. All words are lowercase.

## Examples

| Input | Output | Why |
|---|---|---|
| `3` `4` `5` | `scalene` / `right` | 9 + 16 = 25 |
| `5` `3` `4` | `scalene` / `right` | same sides in another order |
| `2` `2` `3` | `isosceles` / `not right` | two sides equal |
| `7` `7` `7` | `equilateral` / `not right` | all equal |
| `1` `2` `3` | `invalid` | 1 + 2 = 3, a flat triangle |
| `0` `4` `4` | `invalid` | a side of length 0 |
| `-3` `4` `5` | `invalid` | a negative side |

## Constraints

- `-1000000000 <= a, b, c <= 1000000000`
- Use only whole-number arithmetic. Do not use square roots or floats.

## Before you code

Write down, in order, the questions your program must ask, and which question must come first.
Then write your plan as comments at the top of `solution.py`. How will you find the largest side without sorting?
