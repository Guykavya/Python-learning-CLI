## Hint 1

Look at the three bad examples in the statement. In each one, what comes **after** the registered text? Which kind of comparison says "yes" when something follows?

## Hint 2

You are not looking for a clever parser. The rule of the chapter is the opposite: no interpretation at all. What operation on a string and a list of strings answers "is this exact text one of them"?

## Hint 3

```text
registered = client["redirect_uris"]
if redirect_uri not in registered: raise 400
```
