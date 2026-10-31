## Hint 1

Count the brackets in each pattern first: zero groups, one group or two groups? That decides the **shape** of each result before you look at the text.

## Hint 2

`(\w+)=(\d+)` matches `id=7`, `x=10` and `id=42`, so you get three tuples. For `(a)|(b)` on `"ab"`: in the first match only group 1 took part, in the second only group 2. What does the group that did not take part give?

## Hint 3

```
\d* on "a12":
  pos 0: 'a' is not a digit -> empty match ''
  pos 1: '12'
  pos 3 (end): empty match ''
(\d)+ on "123 45": whole matches 123 and 45, group keeps the LAST digit
((\d)\d): outer group = both digits, inner group = first digit
```
