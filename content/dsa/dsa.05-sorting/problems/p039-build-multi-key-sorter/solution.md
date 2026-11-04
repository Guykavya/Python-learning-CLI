## Approach

Treat each rule as a tie-breaker for the previous one. Implement a stable merge sort and plug in a comparison that walks through the rules. Tie on every rule means 'keep the left record first'.

## Code

```python
n = int(input())
rows = []
for _ in range(n):
    name, age, score = input().split()
    rows.append((name, int(age), int(score)))
k = int(input())
rules = []
INDEX = {"name": 0, "age": 1, "score": 2}
for _ in range(k):
    field, direction = input().split()
    rules.append((INDEX[field], direction == "asc"))


def goes_first(x, y):
    for idx, ascending in rules:
        if x[idx] != y[idx]:
            return (x[idx] < y[idx]) == ascending
    return True


def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if goes_first(left[i], right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


for name, age, score in merge_sort(rows):
    print(name, age, score)
```

## Complexity

O(n log n * k) time (each comparison looks at up to `k` rules), O(n) memory, stable.

## Another way

Apply the rules **from last to first** with stable one-key sorts (problem p035's idea): each pass sorts by one rule and the final pass is the first rule. With your own merge sort that means `k` passes. A single pass with a combined comparison is what real databases do.
