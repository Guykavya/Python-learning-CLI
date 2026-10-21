## Hint 1

`any(ch.isdigit() for ch in password)` is `True` if at least one character is a digit.

## Hint 2

`all(ch.isalnum() for ch in password)` checks every character. What does `all` give when
there are no characters?

## Hint 3

Store each check in a variable, print `"yes" if check else "no"`, then use `all` (or `and`)
on the four checks for the verdict.
