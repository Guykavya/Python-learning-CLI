## Hint 1

In `1234567` a comma goes at a gap where the number of digits to the **right** is a multiple of
3 (and more than 0). "The rest of the string is one or more groups of three digits and then the
end" is a lookahead: `(?=(?:\d{3})+$)`. Why is the `$` essential? Try it without.

## Hint 2

Why do you also need "there is a digit just **before** this gap"? Try your pattern on `123`
and on `-123`. Which lookbehind fixes both cases?

For the Indian version: the digits to the right must be three digits plus any number of
**pairs**: `(?:\d\d)*\d{3}`, then the end.

## Hint 3

```
commas(n):        return re.sub(r"(?<=\d)(?=(?:\d{3})+$)", ",", str(n))
commas_indian(n): return re.sub(r"(?<=\d)(?=(?:\d\d)*\d{3}$)", ",", str(n))
```
