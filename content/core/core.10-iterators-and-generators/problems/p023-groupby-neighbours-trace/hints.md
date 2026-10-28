## Hint 1

`groupby` walks the list from left to right and starts a **new group every time the key
changes**. Write the first letters in a row: `a a b a b c`. Where does the key change?

## Hint 2

In the last part, the list comprehension runs `groupby` to the very end **before** any group is
read. A group shares its iterator with `groupby`. When `groupby` moves on to the next key, what
is left in the old group?
