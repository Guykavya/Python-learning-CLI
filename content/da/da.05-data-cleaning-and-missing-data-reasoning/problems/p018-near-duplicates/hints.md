## Hint 1

What are all the pairs `(i, j)` with `i < j` of positions in a list, and how do you generate them with two loops so a
name is never compared with itself or twice? Which function from `difflib` gives the similarity, and what must you do
to the text before you give it to that function? Is the limit itself included?

## Hint 2

```text
keys = [lower-case, single-spaced version of each name]
pairs = []
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        if SequenceMatcher(None, keys[i], keys[j]).ratio() >= threshold:
            pairs.append((i, j))
return pairs                # already in sorted order: i grows, and j grows inside each i
```
For a faster version, reuse one matcher with `set_seq2` / `set_seq1` and skip pairs whose `quick_ratio()` is already too low.
