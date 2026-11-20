# Documents inside SQL

Chapter section 16. When products have very different attributes (a shirt has a size, a phone has a storage capacity), one column holding a **JSON document** can be easier than fifty mostly-empty columns. SQLite (3.38 and newer) reads JSON with `json_extract`. The table:

```sql
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT NOT NULL, attrs TEXT NOT NULL);   -- attrs: a JSON object
INSERT INTO products VALUES (1, 'Shirt', '{"color": "red", "size": "M"}');
```

Write

```python
find_by_attr(db, key, value)      # -> sorted list of product ids
```

returning the ids of the products whose JSON `attrs` has the **top-level key** `key` equal to `value`.

- `value` is a string, an int, a float or a bool (`True` matches JSON `true`). Anything else (including `None`) raises `ValueError`.
- A product **without** the key does not match (a missing key is not "equal to" anything).
- The **key and value must be bound parameters**, never pasted into the SQL. Keys can contain a dot, a space or a quote (`a.b`, `screen size`, `5" screen`) and must be taken literally. A JSON path (`$.key`) cannot express every key, so use the table function **`json_each(attrs)`**, which returns the members of the object as rows with the columns `key` and `value`.

## Example

```python
find_by_attr(db, "color", "red")      # [1, 4]
find_by_attr(db, "in_stock", True)    # ids of products with "in_stock": true
find_by_attr(db, "weight", 0.5)       # numbers compare as numbers
```
