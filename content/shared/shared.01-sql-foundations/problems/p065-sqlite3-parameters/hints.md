## Hint 1

Which attribute of the cursor returned by `execute` holds the id of the row just inserted? Do you need to commit after an `INSERT`?

For `books_between`: how can one SQL text mean "any category" when the parameter is `None`? Think of `:category IS NULL OR ...`.

## Hint 2

```
add_customer: cur = con.execute("INSERT ... VALUES (?, ?)", (name, city)); con.commit(); return cur.lastrowid
find_customer: con.execute("SELECT ... WHERE name = :name ORDER BY customer_id LIMIT 1", {"name": name}).fetchone()
books_between: "... WHERE price BETWEEN :low AND :high AND (:category IS NULL OR category = :category) ORDER BY price, title"
```
