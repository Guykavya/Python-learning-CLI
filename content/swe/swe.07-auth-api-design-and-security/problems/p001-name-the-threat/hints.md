## Hint 1

Ask the "short test" question of the table for each bug: did the attacker **pretend**, **change**, **deny**, **read**, **block** or **gain rights**? Decide what happens **first**; other bad things may follow, but only one letter is the main one.

## Hint 2

Watch the pairs that look alike. Changing a value (`T`) is not gaining rights (`E`) unless the thing changed *is* a right (a role). Reading data you may not read (`I`) is not pretending to be someone (`S`): bug 8 sends no fake identity, it just asks for another object.

## Hint 3

```text
1 price edited         -> data changed            -> T
2 role set to admin    -> more rights than given  -> E
3 logs in as Asha      -> pretends to be Asha     -> S
4 error page with secrets -> reads what it should not -> I
5 20,000 requests/s    -> service unusable        -> D
6 no audit log         -> can deny, no proof      -> R
7 JSON changed on wire -> data changed in transit -> T
8 sees other user's order -> reads what it should not -> I
```
