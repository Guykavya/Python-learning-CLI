## Hint 1

Which names refer to the **same** outer list? `b = a` copies nothing. `a[:]` makes a new outer
list. `copy.deepcopy` copies the inner list too.

## Hint 2

A shallow copy shares the inner list `[2, 3]`. Appending to it through `c` is visible through
`a` and `b`. Replacing a slot (`c[2] = 400`) is not.

## Hint 3

`a += [7]` extends the list that `a` and `b` share. `a = a + [8]` makes a new list and moves
only the name `a`.
