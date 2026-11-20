## Hint 1

`UNIQUE` refuses a new value that **equals** an existing one. How does `NULL` compare with another `NULL`: equal, different, or unknown?

## Hint 2

Insert 4 repeats an exact text; insert 5 differs in the case of one letter, and plain text comparison in SQLite is case-sensitive.

## Hint 3

`''` is a real value (empty text), not `NULL`: the second one collides with the first. Insert 7 is refused.
