## Hint 1

Print `type(e).__name__`, `e.args` and `str(e)` for `KeyError("cake")` and for
`ValueError("x")`. Which one gives you the plain key?

## Hint 2

Check the three cases in the order given: empty `args` first, then `isinstance(err, KeyError)`,
then the general case.

## Hint 3

```
name = type(err).__name__
if not err.args: return name
if isinstance(err, KeyError): return name + ": missing key " + str(err.args[0])
return name + ": " + ", ".join(str(a) for a in err.args)
```
