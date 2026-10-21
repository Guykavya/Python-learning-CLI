## Approach

Run, read, fix one, repeat. The order in which errors appear teaches how Python
works.

1. First run: `SyntaxError: '(' was never closed` on the last line. Nothing
   printed, because the whole file is compiled first.
2. Second run: `Canteen receipt` and `Item: Samosa` print, then
   `TypeError: can only concatenate str (not "int") to str` on the Quantity line.
3. Third run: `NameError: name 'totl' is not defined. Did you mean: 'total'?`.

## Code

```python
item = "Samosa"
price = 15
quantity = 3
total = price * quantity

print("Canteen receipt")
print("Item: " + item)
print("Quantity: " + str(quantity))
print("Total: Rs", total)
print("Thank you!")
```

## Why `"Item: " + item` was fine

`item` is already a `str`. Only `quantity` is an `int`. `+` between two strings
joins them; between a string and an int Python refuses to guess.

## Another way

`print("Quantity:", quantity)`: `print` converts each value to text itself and
puts a space between them.
