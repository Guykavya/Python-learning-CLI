# List or set for membership?

A program reads 200,000 usernames and must report, for each one, whether it was already seen.
A classmate wrote:

```python
seen = []
for _ in range(n):
    name = input()
    if name in seen:
        print("repeat")
    else:
        seen.append(name)
```

It is correct but takes minutes. Changing `seen = []` to `seen = set()` and `append` to `add`
makes it finish in a fraction of a second.

Explain in your own words, in `answer.md`:

1. How `name in seen` works for a list, and its cost in Big-O.
2. Why the whole loop is O(n²) with a list. Estimate the number of comparisons for 200,000 names.
3. How `name in seen` works for a set, and its cost.
4. What the set gives up compared with the list (think about order, duplicates, what can be
   stored, and memory).
5. A case where a list is still the better choice.
