# Insert, select, update, delete in Core

Chapter section 8.3. `solution.py` already defines the table `customers(id, name, city)` (`metadata`, `customers`). Write four functions that take an `Engine` as their first argument:

| Function | What it does | Returns |
|---|---|---|
| `add_many(engine, rows)` | insert all `rows` (a list of dicts with `name` and optional `city`) in **one transaction** | the number of rows inserted (`0` for an empty list: do not call the database) |
| `by_city(engine, city)` | the names of the customers in that city, sorted | a list of strings |
| `rename(engine, customer_id, new_name)` | change one customer's name | the number of rows changed (0 or 1) |
| `remove(engine, customer_id)` | delete one customer | the number of rows deleted (0 or 1) |

Use the statement constructors `insert`, `select`, `update`, `delete` (not strings). **Writes** use `with engine.begin() as conn:` (commit at the end, rollback on error); reads use `engine.connect()`.

## Example

```python
add_many(engine, [{"name": "Asha", "city": "Pune"}, {"name": "Ravi", "city": "Pune"}])    # 2
by_city(engine, "Pune")                      # ["Asha", "Ravi"]
rename(engine, 1, "Asha K.")                 # 1
remove(engine, 99)                           # 0
```
