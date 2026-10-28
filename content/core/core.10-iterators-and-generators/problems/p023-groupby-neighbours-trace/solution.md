## Approach

**Part 1.** The first letters are `a a b a b c`. `groupby` makes a new group at every change, so
there are five groups: `a` (apple, avocado), `b` (banana), `a` (apricot), `b` (blueberry),
`c` (cherry). The letter `a` appears twice as a key.

**Part 2.** After `sorted`, equal first letters sit next to each other:
`apple apricot avocado banana blueberry cherry`. Now there is one group per letter.

**Part 3.** The groups are not lists. Each one is a view into the one shared iterator that
`groupby` reads. To get the next key, `groupby` must read past all items of the current group.
The list comprehension asks for all keys first, so by the time we call `list(group)`, every
group has already been passed over and is empty.

## Output

```text
a ['apple', 'avocado']
b ['banana']
a ['apricot']
b ['blueberry']
c ['cherry']
---
a ['apple', 'apricot', 'avocado']
b ['banana', 'blueberry']
c ['cherry']
---
a []
b []
c []
```

## Complexity

O(n) for each pass, plus O(n log n) for the sort.

## Another way

To keep groups for later, turn each one into a list **at once**:
`saved = [(letter, list(group)) for letter, group in groups]`.
