## Hint 1

A and B each fix one kind of "no city". Which function replaces NULL with something? Which one replaces something with NULL? For C, what must happen first: turning `''` into NULL, or replacing NULL with text?

## Hint 2

```
A: COALESCE(city, 'unknown')
B: NULLIF(city, '')
C: COALESCE( NULLIF(city, ''), 'unknown' )      -- clean first, then default
```

Name each result column `city` with `AS`.
