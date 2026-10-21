## Approach

Read the digits left to right. Each time a new digit arrives, every digit already read moves one place to the
left, which doubles its worth. So the new value is `value * 2 + digit`. This is called **Horner's method**, and
it means you never need to know the length of the string or compute any powers of two.

Validation happens in the same loop: the moment a character is neither `"0"` nor `"1"`, set `valid = False`
and `break`. After the loop, print the value only if every character was fine.

## Trace

Input `1101`:

| ch | value before | value after |
|---|---|---|
| `1` | 0 | 0 * 2 + 1 = 1 |
| `1` | 1 | 1 * 2 + 1 = 3 |
| `0` | 3 | 3 * 2 = 6 |
| `1` | 6 | 6 * 2 + 1 = 13 |

`valid` stays True. Printed: `13`.

## Code

```python
s = input()

value = 0
valid = True
for ch in s:
    if ch == "0":
        value = value * 2
    elif ch == "1":
        value = value * 2 + 1
    else:
        valid = False
        break

if valid:
    print(value)
else:
    print("invalid")
```

## Complexity

One loop round per character: O(L) time for a line of L characters, O(1) extra space.

## Another way

**Right to left with a power of two.** Walk the string from the last index down to 0 (`for i in range(len(s) - 1, -1, -1)`),
keep `power = 1`, add `power` whenever `s[i] == "1"`, and double `power` each step. This matches the "positions are
worth 1, 2, 4, 8" picture exactly and is good for understanding. Horner's left-to-right form is shorter, needs no
index arithmetic, and is how real number parsers work; prefer it. A third option is the `for ... else` pattern:
put `print(value)` in the loop's `else` branch, which runs only when the loop did not `break`.

## Edge cases

- `0` and `000`: value 0.
- 64 ones: 18446744073709551615, exact because Python integers do not overflow.
- One bad character anywhere (first, middle or last) makes the whole line invalid.
