## Approach

`n % 2` is the last (rightmost) binary digit of `n`, and `n // 2` removes that digit, exactly like `% 10` and
`// 10` do for decimal digits. Repeating this produces the digits from right to left, so each new digit is
put **in front** of the string built so far: `result = str(n % 2) + result`.

For `n = 0` the loop would not run at all and print an empty line, so 0 is handled on its own.

## Trace

Input `13`:

| n before | n % 2 | result after | n after |
|---|---|---|---|
| 13 | 1 | `"1"` | 6 |
| 6 | 0 | `"01"` | 3 |
| 3 | 1 | `"101"` | 1 |
| 1 | 1 | `"1101"` | 0 |

Printed: `1101`.

## Code

```python
n = int(input())

if n == 0:
    print("0")
else:
    result = ""
    while n > 0:
        result = str(n % 2) + result
        n //= 2
    print(result)
```

## Complexity

One loop round per binary digit: about log2(n) rounds, at most 60 for `n <= 10^18`. So O(log n) time.
The string has O(log n) characters.

## Another way

**Highest power of two first.** Find the largest power of two `p` with `p <= n` (start at 1 and double while
`p * 2 <= n`). Then walk `p` down to 1, halving each time: if `n >= p` write `1` and subtract `p`, otherwise
write `0`. This produces the digits left to right, so you can add each one to the **end** of the string or even
print them one at a time with `end=""`. It mirrors how people convert by hand with a table of powers of two.
The division method is shorter and works for any base: replace 2 with 8 or 16 (plus letters for 10 to 15).

## Edge cases

- `n = 0`: prints `0`, not an empty line.
- Powers of two such as 1024: a 1 followed by zeros.
- `n = 10^18`: 60 digits; Python integers handle it exactly.
