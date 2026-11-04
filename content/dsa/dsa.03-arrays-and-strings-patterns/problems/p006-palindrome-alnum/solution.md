## Approach

Two pointers from both ends. Each pointer first skips characters that do not count; then the two characters that do
count are compared without case. The loop ends when the pointers meet, which means every pair matched.

## Code

```python
def is_pal(s):
    i, j = 0, len(s) - 1
    while i < j:
        while i < j and not s[i].isalnum():
            i += 1
        while i < j and not s[j].isalnum():
            j -= 1
        if s[i].lower() != s[j].lower():
            return False
        i += 1
        j -= 1
    return True


t = int(input())
for _ in range(t):
    print("yes" if is_pal(input()) else "no")
```

## Complexity

O(length) per line: each pointer moves only inwards, so every character is looked at at most once. O(1) extra memory.

## Another way

Clean first, then compare: `c = "".join(ch.lower() for ch in s if ch.isalnum())` and test `c == c[::-1]`.
It is also O(length) but builds two new strings. The two-pointer version is the pattern you need when building a
copy is not allowed.
