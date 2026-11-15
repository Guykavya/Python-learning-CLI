## Hint 1

Does the order of the two steps matter? What would happen to book 2 if the delete ran *after* the delivery was added?

Which clause turns "insert fails because the key exists" into "update that row instead"? How do you refer to the value you were trying to insert?

## Hint 2

```
DELETE FROM stock WHERE qty = 0;

INSERT INTO stock (book_id, qty)
SELECT book_id, SUM(qty) FROM incoming GROUP BY book_id
ON CONFLICT (book_id) DO UPDATE SET qty = qty + excluded.qty;
```
