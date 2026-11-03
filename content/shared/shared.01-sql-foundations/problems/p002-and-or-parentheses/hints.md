## Hint 1

Say the condition in two parts: which categories are allowed, and what the price must be. Which part
must hold for every row, whatever the category?

## Hint 2

```
WHERE ( <category is fiction> OR <category is mystery> )
  AND <price is below 13>
```

Try it without the parentheses on dataset A. Which extra book appears, and why?
