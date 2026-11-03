## Hint 1

When the f-string is evaluated, is the user's text still "data"? Look at the final SQL string in the second call: what does `--` do to the rest of the line, and which part of the check disappeared?

## Hint 2

For question 3: what is a placeholder allowed to stand for, a value or a piece of the query's structure? Think about when the database *parses* the statement versus when it receives the values. Then: how can a program that must choose a column name do it safely (a fixed list of allowed names)?
