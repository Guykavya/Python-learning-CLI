## Code

```python
low = input().casefold()
a = low.count("a")
e = low.count("e")
i = low.count("i")
o = low.count("o")
u = low.count("u")
print(f"a: {a}")
print(f"e: {e}")
print(f"i: {i}")
print(f"o: {o}")
print(f"u: {u}")
print(f"total: {a + e + i + o + u}")
```

## Cost

Five `count` calls walk the text five times. For a line that is nothing. For a huge file, a single loop that looks at each character once would be better; you will write that in core.07.

## Another way

The total alone can be found in one step: delete everything that is not a vowel... which needs a loop or regular expressions. Or: `len(low) - len(low.translate(str.maketrans("", "", "aeiou")))`, the number of characters removed when deleting vowels.
