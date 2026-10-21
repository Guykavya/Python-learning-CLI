# Why is `in` slow on a list?

A classmate wrote this program to count how many words of an essay are in a dictionary of valid words:

```python
valid = input().split()          # 200000 valid words
essay = input().split()          # 100000 words
good = 0
for word in essay:
    if word in valid:
        good += 1
print(good)
```

It works on the small test file but on the real data it runs for many minutes. Changing one line,
`valid = set(input().split())`, makes it finish in a fraction of a second.

Measured on this machine, looking up a value that is **not** present:

| size | `x in list` | `x in set` |
|---|---|---|
| 1,000 | 5.6 microseconds | 0.07 microseconds |
| 10,000 | 50 microseconds | 0.07 microseconds |
| 100,000 | 556 microseconds | 0.07 microseconds |
| 1,000,000 | 6,283 microseconds | 0.08 microseconds |

In `answer.md`, explain in plain words:

1. What Python does to answer `word in valid` when `valid` is a list. Use the table: how does the time change
   when the list gets 10 times bigger, and what is the Big-O?
2. What the whole program's complexity is with a list, in terms of `n` (valid words) and `m` (essay words),
   and roughly how many comparisons that is here.
3. How a set can answer in the same time whatever its size (the idea of hashing, in your own words), and what the
   program's complexity becomes with the set. Include the cost of building the set.
4. One situation where a list is still the right choice, and one thing a set cannot do that a list can.
