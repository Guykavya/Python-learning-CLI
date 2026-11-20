## Hint 1

Two independent questions: (1) is the *failure* temporary? (2) is repeating the *request* harmless? Both must be yes.

## Hint 2

Write the two questions as two small conditions first, then combine them. What does `status is None` mean for the first question?

## Hint 3

```text
safe = method.upper() in IDEMPOTENT or has_idempotency_key
transient = status is None or status in {408, 429, 500, 502, 503, 504}
return safe and transient
```
