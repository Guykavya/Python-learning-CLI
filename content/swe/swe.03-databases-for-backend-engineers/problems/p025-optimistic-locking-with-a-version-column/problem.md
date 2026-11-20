# Optimistic locking with a version column

Chapter section 7.4. Two editors open the same product page (price Rs. 100, version 1). One saves a new price. If the second then saves **their** form, they would silently overwrite the first change (a lost update). With **optimistic locking** each row has a `version`; a save says "I edited version N", and succeeds only if the row is **still** at version N.

```sql
CREATE TABLE products (id INTEGER PRIMARY KEY, price_paise INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 1);
```

Write `update_price(db, product_id, new_price_paise, seen_version)`:

- one `UPDATE` that sets the price **and** increases `version` by 1, only `WHERE id = ? AND version = ?`;
- return `True` if a row was changed, `False` if not (the row is at another version, or does not exist);
- commit the change when it succeeded; a failed attempt changes nothing.

## Example

```python
# product 1: price 10000, version 1
update_price(db, 1, 12000, seen_version=1)    # True  -> price 12000, version 2
update_price(db, 1, 9000, seen_version=1)     # False -> still 12000, version 2 (the second editor lost the race)
```
