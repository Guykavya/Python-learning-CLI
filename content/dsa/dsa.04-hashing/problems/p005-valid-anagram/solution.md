## Approach

Same characters with the same counts means the two **frequency tables are equal**. Build a table for each string and
compare them. Checking the lengths first rejects many pairs immediately.

## Code

```python
s = input().strip()
t = input().strip()

def table(word):
    count = {}
    for ch in word:
        count[ch] = count.get(ch, 0) + 1
    return count

print("YES" if table(s) == table(t) else "NO")
```

Dictionary `==` compares keys and values and ignores order, so the order of first appearance does not matter.

## Complexity

O(n + m) time, O(k) memory for `k` distinct characters.

## Another way

`sorted(s) == sorted(t)` is correct and simple: anagrams sort to the same list. It costs O(n log n). The counting
version is O(n), which is why it is the standard answer.
