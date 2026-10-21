## Hint 1

At position `j` you need some earlier `i` with `a[i] == t - a[j]`. So the question is "have I already seen the
value `t - a[j]`, and where?" Which structure answers "where did I see this value?" in O(1)?

## Hint 2

Keep a dict from value to position. Scan `j` from left to right; before adding `a[j]` to the dict, look up
`t - a[j]`. Looking up before adding makes sure a value does not pair with itself.

## Hint 3

For the tie rule, the first `j` where the lookup succeeds is the smallest `j`. For the smallest `i`, store only the
**first** position of each value: add `a[j]` to the dict only if it is not already there.
