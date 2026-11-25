## Hint 1

Think of one customer's life: a new phone, a shared family phone, a number that used to belong to somebody else. In each case,
does the phone number still point at exactly one person? Then ask the opposite question about an arbitrary `customer_id`.

## Hint 2

```text
paragraph 1: three or more ways the natural key breaks (changes, reused, shared, formatted differently)
paragraph 2: the surrogate key is stable; but it is meaningless, so duplicate people stay duplicate
paragraph 3: keep a uniqueness rule on the natural columns, because the surrogate key does not give it
```
