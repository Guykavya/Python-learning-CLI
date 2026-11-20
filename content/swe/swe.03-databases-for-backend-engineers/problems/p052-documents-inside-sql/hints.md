## Hint 1

You could read one key with `json_extract(attrs, '$.color')`, which returns `NULL` when the key is missing. But how would you write the path of a key such as `5" screen`? Is there a way to get the keys as **data** instead of as part of a path?

## Hint 2

The table function `json_each(p.attrs)` gives one row per top-level member, with columns `key` and `value`. Join it with the products table: `FROM products p, json_each(p.attrs) j`.

## Hint 3

```text
SELECT DISTINCT p.id FROM products p, json_each(p.attrs) j WHERE j.key = ? AND j.value = ? ORDER BY p.id     params (key, value)
```
