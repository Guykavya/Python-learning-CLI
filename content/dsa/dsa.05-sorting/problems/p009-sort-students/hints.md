## Hint 1

You need one sort with two criteria, one descending and one ascending. What can the key function return so that both are handled together?

## Hint 2

Return a tuple `(-score, name)`. Python compares tuples position by position, and negating the score turns 'highest first' into 'smallest first'.

## Hint 3

```
students = [(name, int(score)) ...]
students.sort(key=lambda s: (-s[1], s[0]))
print each
```
