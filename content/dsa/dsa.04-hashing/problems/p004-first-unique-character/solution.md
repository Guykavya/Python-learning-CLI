## Approach

The answer depends on how often a character occurs in the **whole** string, so you cannot decide while reading it once.
Count first, then scan again from the left and report the first index whose character has count 1.

## Code

```python
s = input().strip()

count = {}
for ch in s:
    count[ch] = count.get(ch, 0) + 1

answer = -1
for i, ch in enumerate(s):
    if count[ch] == 1:
        answer = i
        break
print(answer)
```

## Complexity

O(n) time and O(1) memory (at most 26 keys).

## Another way

For each index test `s.count(s[i]) == 1`. It is short but each `count` call scans the string, so it is O(n * 26)
at best on distinct letters and O(n^2) in general. Or `s.find(ch) == s.rfind(ch)` for each letter of the alphabet.
