# Two numbers that make the target

Read a list of `n` integers and a target `t`. Find two **different positions** `i < j` (counting from 1) with
`a[i] + a[j] == t`.

If there are several such pairs, choose the one with the **smallest `j`**; if there are still several, the one
with the smallest `i`. Print `i j`. If there is no pair, print `none`.

`starter.py` does this correctly by trying every pair. Make it fast.

## Input

- Line 1: `n` and `t`, separated by a space.
- Line 2: `n` integers.

## Output

One line: `i j`, or `none`.

## Examples

| Input | Output | Why |
|---|---|---|
| `5 9` / `2 7 11 15 -2` | `1 2` | 2 + 7 = 9 |
| `4 6` / `3 1 3 5` | `1 3` | 3 + 3 = 6 (positions 1 and 3); 1 + 5 also works but j = 4 is later |
| `3 10` / `5 1 2` | `none` | a value cannot pair with itself |
| `4 4` / `2 2 2 2` | `1 2` | smallest j is 2, and then the only i is 1 |

## Constraints

- `1 <= n <= 200000`
- every value and `t` are between `-10^9` and `10^9`

Use `input()` without a prompt message.

## Before you code

When you are standing at position `j` and see the value `a[j]`, which value do you need to have seen earlier?
