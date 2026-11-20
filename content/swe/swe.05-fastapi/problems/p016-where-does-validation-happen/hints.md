## Hint 1

Separate the **interpreter** from the **framework**. What does `def double(n: int)` do with `"ab"` in plain Python (section 5.1)? Now: who calls your endpoint function, and what does that caller do with the signature before calling it?

## Hint 2

Draw the five boxes of section 6.1 and mark where each status comes from: 404/405, 422 `json_invalid`, 422 field errors, your own `HTTPException`, 500. For "username taken": could Pydantic know that from the JSON alone, without the database? Which status means "conflicts with the current state of the server"?

## Hint 3

```text
1. interpreter ignores hints; FastAPI reads the signature -> Pydantic validators
2. routing -> read/parse -> validate (all errors) -> endpoint -> response filter
   validation is before the endpoint: inside it, values are already clean
3. 422 = client sent data that breaks the declared rules; fix the request; use type + loc
4. "taken" needs the database = business rule -> 409 from HTTPException; 422 is no bug (no alert)
```
