## Hint 1

What pattern matches "one or more digits"? Try `re.findall(r"[0-9]+", "a 12 b 5")` in the REPL. What type are the items in the result?

## Hint 2

The sign is optional. Which quantifier means "zero or one of the previous thing"? Put it after a `-` in front of the digits part.

## Hint 3

```
numbers(s):
    texts = re.findall(r"-?[0-9]+", s)
    return [int(t) for t in texts]
```
