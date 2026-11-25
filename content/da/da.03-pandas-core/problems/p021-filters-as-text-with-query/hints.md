## Hint 1

Write the condition as one English-looking line. How do you tell `query` that `min_qty` is a variable of your function and not a column? How do you write a column name that contains a space?

## Hint 2

```text
df.query("qty >= @min_qty and region == @region and `unit price` > 0")
```
`@name` reads a variable from the surrounding Python code; backticks make a name with a space legal.
