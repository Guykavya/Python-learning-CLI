## Hint 1

What does `city <> 'Pune'` give for a row whose city is NULL: true, false or unknown? Does `WHERE` keep unknown rows? What extra condition would catch exactly those rows?

## Hint 2

```
WHERE <city differs from 'Pune'>
   OR <city is unknown>
```

Check the result has all the NULL-city customers.
