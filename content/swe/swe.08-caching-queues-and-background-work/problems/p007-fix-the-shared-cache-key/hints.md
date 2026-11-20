## Hint 1

Write the sequence: Asha asks for product 1 (miss, the member price is stored under some key), then Ravi asks for product 1. Which key does Ravi's request look up? What is stored there?

## Hint 2

Rule from the chapter: everything the answer depends on belongs in the key. List the inputs of `db.price(...)`. Then ask: should the user's *name* be in the key? (What would that do to the number of database reads for 10,000 public users?)

```text
key = f"price:{product_id}:{tier}"
```
