## Hint 1

For a list, `x += y` changes the list in place. For a tuple or a string, which cannot change,
`x += y` builds a new object and moves the name.

## Hint 2

`x * 2` on a list of lists repeats **references** to the inner list.

## Hint 3

`m = [n, n]` holds two references to the list `n`. `n += [2]` changes that list; `n = n + [3]`
makes a new one and moves only `n`.
