# Any repeats?

Read a list of numbers and print `YES` if some value appears more than once, otherwise `NO`.

`starter.py` already does this by comparing every pair of positions. It is correct, but for 100000 numbers it
makes about five billion comparisons. Make it fast.

## Input

- Line 1: an integer `n`.
- Line 2: `n` integers separated by spaces.

## Output

`YES` or `NO`.

## Examples

| Input | Output | Why |
|---|---|---|
| `5` / `3 1 4 1 5` | `YES` | 1 appears twice |
| `4` / `10 20 30 40` | `NO` | all different |
| `1` / `7` | `NO` | one number cannot repeat |
| `3` / `-2 2 -2` | `YES` | -2 appears twice; 2 and -2 are different |

## Constraints

- `1 <= n <= 200000`
- every value is between `-10^9` and `10^9`

Use `input()` without a prompt message.

## Before you code

What would you do with a pencil if someone read the numbers out to you one by one, and you had to shout as
soon as you heard a repeat? What would you write down?
