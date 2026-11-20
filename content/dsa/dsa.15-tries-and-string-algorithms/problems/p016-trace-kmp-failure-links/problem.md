# Trace KMP failure links

KMP (chapter section 11) searching the pattern `aabaab` in the text `aaabaaab`. The prefix function of the pattern is given. Each line shows `k` before the letter, every fallback, and `k` after the letter. Predict **exactly** what this program prints. Do not run it.

```python
text, pattern = "aaabaaab", "aabaab"
pi = [0, 1, 0, 1, 2, 3]
m = len(pattern)
k = 0
found = []
for i, ch in enumerate(text):
    steps = [str(k)]
    while k > 0 and ch != pattern[k]:
        k = pi[k - 1]
        steps.append(str(k))
    if ch == pattern[k]:
        k += 1
    print(f"i={i} {ch}: k " + " -> ".join(steps) + f" => {k}")
    if k == m:
        found.append(i - m + 1)
        k = pi[k - 1]
print("found:", found)
```

Write your answer in `answer.txt`, one printed line per line: eight `i=` lines, then the `found:` line (check carefully whether anything is found).

## How to work

1. Write the pattern with its indices and the given `pi` under it: `a a b a a b` / `0 1 0 1 2 3`.
2. For each text letter, start from the current `k`. While `k > 0` and the letter differs from `pattern[k]`, fall back with `k = pi[k - 1]` and write the new `k` after an arrow.
3. If the letter equals `pattern[k]`, `k` grows by 1. That is the number after `=>`.
4. If `k` reaches 6, a match ends here. Does that happen?

## After you answer

1. At `i = 6` the state falls twice. Which matched text was `aabaa`, and which borders does KMP try before it can continue?
2. The text never contains the pattern. At which start position does the text come closest, and how many letters match there?
3. The text pointer `i` never moves back. How many letter comparisons does the program make in total?
