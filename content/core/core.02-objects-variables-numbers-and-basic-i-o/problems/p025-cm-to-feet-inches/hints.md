## Hint 1

The starter prints things like `5.0 ft 8.89... in`. Where should the rounding happen: before or after splitting?

## Hint 2

`round(x)` with one argument returns an `int`. Then `divmod(total, 12)` gives `(feet, inches)` as ints.

## Hint 3

```
total_inches = round(cm / 2.54)
feet, inches = divmod(total_inches, 12)
print(f"{feet} ft {inches} in")
```
