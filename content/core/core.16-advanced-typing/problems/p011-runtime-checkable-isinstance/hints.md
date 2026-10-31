## Hint 1

Which decorator from `typing` allows `isinstance(x, HasArea)`? What error do you get without it? Once both protocols have it, the functions are filters over the input items.

## Hint 2

`isinstance(x, Named)` is `True` if `x` has an attribute called `name`, whatever it holds: a string, a number, even a method. So for `names_of` you need a second test on the value itself. How do you test that something is a `str`? Be careful with the order of the two tests: what happens if you read `x.name` before you know it exists?

## Hint 3

```
total_area(things):  total = 0.0 ; for t in things: if isinstance(t, HasArea): total += t.area() ; return total
names_of(things):    for t in things: if isinstance(t, Named) and isinstance(t.name, str): collect t.name
classify(t):         a = isinstance(t, HasArea) ; n = isinstance(t, Named)
                     both / area / name / neither
```
