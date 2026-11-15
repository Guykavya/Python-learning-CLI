## Hint 1

Bug 1 is about ties. When `left[i]` and `right[j]` have the same key, which one must be taken first to keep the input order? Look at the comparison sign.

## Hint 2

Bug 2: the loop ends when one half is used up. The other half still has values; `starter.py` copies the leftover of only one half.

## Hint 3

Bug 3: look at the two slices of the recursive calls. Together they must cover **every** element exactly once.
