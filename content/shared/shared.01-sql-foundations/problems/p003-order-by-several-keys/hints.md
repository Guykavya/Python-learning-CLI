## Hint 1

Which sort key is most important? What happens to the second key when two rows have the same first key?
Where does the word `DESC` go: after the whole list, or after one key?

## Hint 2

```
SELECT category, title, price FROM books
ORDER BY <key 1>, <key 2> DESC, <key 3>
```

`DESC` belongs to the key it follows only.
