## Approach

Sorting puts letters into a standard order. Two phrases with the same letters (and the same number of each) sort to the same string. That sorted string is the phrase's **key**.

## Code

```python
import string

table = str.maketrans("", "", string.punctuation + string.whitespace)
key1 = "".join(sorted(input().casefold().translate(table)))
key2 = "".join(sorted(input().casefold().translate(table)))
print(f"Key 1: {key1}")
print(f"Key 2: {key2}")
print(f"Anagrams: {key1 == key2}")
```

## Why casefold before sorting

Sorting compares code points, and all uppercase ASCII letters come before lowercase ones. Without casefolding, `D` and `d` would land in different places.

## Another way

Counting letters with a dictionary (core.05) or `collections.Counter` also works, and is faster for very long texts because sorting takes slightly more than linear time.
