## Hint 1

For each request, find the **first** line of code that can raise an error. The dependency `current_user` always runs first: which requests does it stop?

## Hint 2

Request 3: the token is valid, so the dependency passes. Then the function looks for order 1. Does order 1 exist? Whose is it? Compare the condition `order is None or order["owner"] != user[0]` for the case "exists but belongs to ada" with the case "does not exist". Request 4: which line checks the role, and what is `user[1]` for ada?

## Hint 3

```text
1 no header -> "" -> not a token       -> 401
2 unknown token                        -> 401
3 bo asks for ada's order 1            -> owner differs -> 404
4 ada (customer) on /admin/users       -> role check    -> 403
5 order 99 does not exist              -> 404
6 ada asks for her own order 1         -> 200, prints the owner
```
