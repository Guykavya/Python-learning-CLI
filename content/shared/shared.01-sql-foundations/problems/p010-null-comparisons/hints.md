## Hint 1

For each query, go through the five customers and write true, false or unknown for the condition. Only rows with *true* are kept. What is `NULL = NULL`? What is `NULL <> 'Pune'`?

## Hint 2

```
Q3:  city = 'Pune' OR city = NULL
     Asha: true OR unknown  -> true
     Ben : unknown OR unknown -> unknown
     Chen: false OR unknown   -> unknown   (not false!)
Q4:  city <> 'Pune' AND city <> NULL
     false AND unknown = false;  true AND unknown = unknown
```

So can Q4 ever be true?
