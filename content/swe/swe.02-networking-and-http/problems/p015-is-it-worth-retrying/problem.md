# Is it worth retrying?

Chapter sections 9.2, 10.4 and 21.2. A request failed. Should the client try again? Write

```python
worth_retrying(method, status, has_idempotency_key=False)
```

- `method` is the HTTP method (any case). `status` is the status code of the response, or **`None`** when there was no response at all (connection error, read timeout, reset).
- A request is **safe to repeat** when the method is idempotent (`GET`, `HEAD`, `OPTIONS`, `TRACE`, `PUT`, `DELETE`) **or** it carries an idempotency key.
- A failure is **transient** when `status` is `None`, or one of `408, 429, 500, 502, 503, 504`.
- Return `True` only when the failure is transient **and** the request is safe to repeat. Everything else (a `404`, `400`, `401`, `403`, `422`, any `2xx` or `3xx`, `501`) is `False`.

## Example

```python
worth_retrying("GET", 503)                              # True
worth_retrying("POST", 503)                             # False: the server may have done the work
worth_retrying("POST", 503, has_idempotency_key=True)   # True
worth_retrying("GET", 404)                              # False: repeating cannot help
worth_retrying("PUT", None)                             # True: connection error, PUT is idempotent
```
