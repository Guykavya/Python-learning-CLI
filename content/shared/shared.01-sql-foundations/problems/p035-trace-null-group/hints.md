## Hint 1

Sort the six customers into piles by `city` (NULL is its own pile). In each pile, count the rows, then count only those whose `email` is
not NULL, then count only those whose `city` is not NULL. What is `COUNT(city)` for the pile whose city is NULL?

## Hint 2

```
pile NULL : Bala (b@x), Dev (NULL)            -> n=?  with_email=?  with_city=?
pile Goa  : Esha (e@x)                         -> n=?  ...
pile Pune : Asha (a@x), Chitra (NULL), Farid   -> n=?  ...
order: NULL first, then Goa, then Pune
```
