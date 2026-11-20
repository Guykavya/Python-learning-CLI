# Prefix function by hand

The prefix function of chapter section 10, with a print for every position. `path` lists the value of `k` before the step and every value it falls back to. Predict **exactly** what this program prints. Do not run it.

```python
s = "abacabab"
pi = [0] * len(s)
k = 0
for i in range(1, len(s)):
    path = [k]
    while k > 0 and s[i] != s[k]:
        k = pi[k - 1]
        path.append(k)
    if s[i] == s[k]:
        k += 1
    pi[i] = k
    print(i, s[i], path, k)
print(pi)
```

Write your answer in `answer.txt`, one printed line per line: seven lines for `i = 1` to `7`, then the list `pi`.

## How to work

1. Write the string with its indices: `a b a c a b a b` at 0 to 7, and an empty `pi` row under it with `pi[0] = 0`.
2. For each `i`, start from the current `k` (the border length so far). Compare `s[i]` with `s[k]`, the letter that would **extend** the border.
3. On a mismatch with `k > 0`, fall back: `k = pi[k - 1]`, and add the new `k` to `path`. Repeat until a match or `k = 0`.
4. On a match, `k` grows by 1. Write `pi[i] = k`.

## After you answer

1. At `i = 7` the border falls from 3 to 1 and then grows to 2. Name the borders: which string of length 3 could not be extended, and which string of length 2 is the final border?
2. What is the longest border of the whole string, and what is its smallest period (`n - pi[n - 1]`)? Check the period on the string itself.
3. How many letter comparisons did the program make in total? Is it below `2n`?
