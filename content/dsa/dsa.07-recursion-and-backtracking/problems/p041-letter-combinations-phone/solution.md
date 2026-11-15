## Approach

Choose, explore, un-choose with one level per digit. Nothing is forbidden, so every leaf is an answer; the number of answers is the product of the letter counts. The empty input is a special case required by the problem.

## Code

```python
PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
         "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def letter_combinations(digits):
    if not digits:
        return []
    result, path = [], []

    def go(i):
        if i == len(digits):
            result.append("".join(path))
            return
        for ch in PHONE[digits[i]]:
            path.append(ch)
            go(i + 1)
            path.pop()

    go(0)
    return result
```

## Complexity

`O(4^n * n)` in the worst case (all 7s and 9s), depth `n`.

## Another way

Build level by level without recursion: start with `[""]` and for each digit replace the list with `[s + ch for s in current for ch in PHONE[d]]`.
