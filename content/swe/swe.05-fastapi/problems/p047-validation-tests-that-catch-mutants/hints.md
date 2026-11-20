## Hint 1

A mutant that changes a limit by one step (100 → 101) behaves exactly like the correct app for every value **except one**. Which single title length is accepted by the mutant but refused by the correct app? That value is the only test that catches it. This is why testers love **boundary values**.

## Hint 2

For each rule of the table write two cases: the value **on** the limit (valid, 201) and the value **one step past** it (invalid, 422).

```text
title length:  1 -> 201,  0 ("") -> 422,  100 -> 201,  101 -> 422
priority:      1 -> 201,  0 -> 422,  5 -> 201,  6 -> 422
unknown field: {"title": "a", "owner": "x"} -> 422
```
Make every invalid payload break **only one** rule; otherwise you cannot tell which rule refused it.

## Hint 3

```text
CASES = [
  ({"title": "x"}, 201), ({"title": "x" * 100}, 201),
  ({"title": ""}, 422), ({"title": "x" * 101}, 422),
  ({"title": "a", "priority": 1}, 201), ({"title": "a", "priority": 5}, 201),
  ({"title": "a", "priority": 0}, 422), ({"title": "a", "priority": 6}, 422),
  ({"title": "a", "owner": "asha"}, 422),
  ({"priority": 2}, 422),
]
```
