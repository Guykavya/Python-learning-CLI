## Hint 1

How many writes does `print(x)` do per call? (Two: the text and the newline.) What if you built **one** big string first?

## Hint 2

`"\n".join(list_of_strings)` joins strings with a newline in between. You need `str` of every number first, because `join` accepts only strings.

## Hint 3

```text
data = read all tokens
out = [str(x * x) for x in numbers]
print("\n".join(out))
```
