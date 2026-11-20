## Hint 1

Section 3.1: a simple-typed parameter that is not in the path comes from the **query string**. How do you tell FastAPI "this one is a header" or "this one is a cookie"? What does the `Annotated[<type>, <where>()] = None` pattern look like?

## Hint 2

Header names: FastAPI converts `_` to `-` and ignores case, so the Python name `x_request_id` matches `X-Request-ID`. A header sent twice is read with a **list** type. Cookies are matched by their exact name.

## Hint 3

```text
user_agent:   Annotated[str | None, Header()] = None
x_request_id: Annotated[str | None, Header()] = None
x_token:      Annotated[list[str] | None, Header()] = None
session:      Annotated[str | None, Cookie()] = None
return {..., "tokens": x_token or [], "logged_in": session is not None}
```
