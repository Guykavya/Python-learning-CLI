## Hint 1

For A: where does the wildcard go if the letter is at the start? For B: what replaces a chain of `OR`s? For C: is a price of exactly 18.00 allowed?

## Hint 2

```
A: WHERE title LIKE '<letter><wildcard>'
B: WHERE category IN (<value>, <value>)
C: WHERE price BETWEEN <low> AND <high>
```
