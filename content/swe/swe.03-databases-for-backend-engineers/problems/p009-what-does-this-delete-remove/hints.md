## Hint 1

For each delete, follow the arrows: what references the deleted row, and what does that foreign key's rule say? `CASCADE` deletes the children, `SET NULL` keeps them with an empty link, `RESTRICT` refuses.

## Hint 2

Statement 1 removes customer 1. Orders 10 and 11 belong to it: they go, and **their** lines go too (a cascade can chain). The tickets of customer 1 stay but their `customer_id` becomes `NULL`.

## Hint 3

Statement 2: order 12 is referenced by invoice 1 with `RESTRICT`: error, nothing changes. Statement 3 removes the invoice. Statement 4 now works and cascades to the one line of order 12.
