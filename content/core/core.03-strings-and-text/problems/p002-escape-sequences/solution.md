## Approach

Each line needs a different escape:

| Line | Problem | Solution |
|---|---|---|
| 1 | both quote types | wrap in single quotes and write `\'` |
| 2 | `\n` and `\t` would become a newline and a tab | raw string, or `\\` |
| 3 | a real tab | `\t` |
| 4 | a symbol you may not be able to type | `\u20b9` |
| 5 | tab plus arrows | `\t` with `\u2192` and `\u2190` |

## Code

```python
print('She said "It\'s fine"')
print(r"C:\new\table")
print("Name:\tAsha")
print("Price: \u20b9500")
print("Tab\u2192\t\u2190Tab")
```

## Why `\u20b9500` is safe

A `\u` escape always takes exactly four hex digits, so `\u20b9` ends before `500`. With `\x`, which takes two digits, you would need to be just as careful.

## Another way

A triple-quoted string can hold both quote types without escapes: `print("""She said "It's fine\"""")` works, but the ending is awkward. Escaping one quote is cleaner.
