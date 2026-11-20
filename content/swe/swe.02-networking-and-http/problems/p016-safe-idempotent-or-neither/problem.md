# Safe, idempotent, or neither?

A tiny server keeps three things, all empty or zero at the start:

- `orders`: a list; **`POST /orders`** appends one order and answers `201`.
- `a`: a dictionary; **`PUT /a/1`** with `{"v": 7}` sets `a["1"] = 7`. It answers `201` if the key did not exist and `200` if it did.
- `counter`: a number; **`PATCH /counter`** with `{"add": 1}` adds to it and answers `200`.

Also: **`DELETE /a/1`** removes the key and answers `204`; if the key does not exist it changes nothing and answers `404`. **`GET`** changes nothing: `GET /a/1` answers `200` if the key exists, else `404`; `GET /orders` answers `200`.

Ten calls arrive, one after the other:

```text
 1. GET    /a/1
 2. POST   /orders        {"qty": 2}
 3. POST   /orders        {"qty": 2}
 4. PUT    /a/1           {"v": 7}
 5. PUT    /a/1           {"v": 7}
 6. PATCH  /counter       {"add": 1}
 7. PATCH  /counter       {"add": 1}
 8. DELETE /a/1
 9. DELETE /a/1
10. GET    /orders
```

After **each** call write the status code and the state of the server:

```text
1: status=<code> orders=<number of orders> a1=<value of a["1"] or -> counter=<number>
```

Use `-` when `a["1"]` does not exist. Do not run anything.

## After you answer

1. Which pairs of identical calls left the state the same the second time (idempotent)? Which changed it again?
2. A `PUT` and a `DELETE` repeated give different **status codes**, yet the state is the same. Why is that still "idempotent"?
3. Which methods in this list are **safe** (they never change state)?
