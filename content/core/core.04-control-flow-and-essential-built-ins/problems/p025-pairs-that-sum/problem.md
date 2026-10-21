# Pairs that sum to a target

Read a line of whole numbers separated by spaces, then a target number. Print every pair of
**different positions** `i < j` whose numbers add up to the target, as `a + b`, in order of
`i` and then `j`. Finally print `Pairs: N`.

**Example**

Input:
```
3 5 2 4 3
6
```
Output:
```
3 + 3
2 + 4
Pairs: 2
```

(Positions 0 and 4 hold 3 and 3; positions 2 and 3 hold 2 and 4. A number is never paired
with itself, so position 0 alone does not make 3 + 3.)
