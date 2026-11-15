## Hint 1

For each customer id, compare it with every id in the list (1, 1, 2, NULL). Is there a value equal to it (then `IN` is true and
`NOT IN` is false)? If not, is every comparison false, or is one of them unknown because of the NULL?

## Hint 2

```
Asha  (1): 1 is in the list -> IN true  -> NOT IN = ?
Bala  (2): 2 is in the list -> ?
Chitra(3): no equal value; 3 = NULL is unknown -> NOT IN = ?
Dev   (4): same as Chitra
NOT EXISTS looks for ROWS with o.customer_id = c.customer_id; a NULL never equals anything, so it just finds no row.
```
