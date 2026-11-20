## Hint 1

A returned string is wrapped in a `Response` with default status and default content type. Which are they? (Section 5.1 has a table of what each return shape becomes.)

## Hint 2

The second and third items of a tuple are the status and a dict of headers. A header you give **replaces** the default one of the same name. A returned dict goes through `jsonify`; remember how Flask writes JSON by default (key order, spaces).

## Hint 3

```text
1  string               -> 200, text/html; charset=utf-8
2  (string, 201)        -> 201, same type
3  (string, 418, {Content-Type: text/plain, ...})  -> header replaced exactly as written
4  dict                 -> 200, application/json, keys sorted, no spaces after : and ,
5  ("", 204)            -> 204, default type, empty body
```
