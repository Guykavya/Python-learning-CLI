# Fix the fuel cost calculator

A classmate wrote a program to work out the fuel for a trip. It has several bugs. Your job is
to **fix** `starter.py` (copy it into `solution.py` first) so that it follows the specification.

**Specification.** Read three lines:

1. the distance in km (decimals allowed, like `120.5`)
2. the mileage in km per litre (decimals allowed)
3. the fuel price per litre in rupees (like `102.86`)

Compute, all with `Decimal` built from the input text:

- `litres = distance / mileage`
- `cost = litres * price`

Print, each rounded to 2 decimals with ROUND_HALF_UP:

```
Litres: <litres>
Cost: <cost>
```

The cost uses the **unrounded** litres; round only for printing.

**Example**

Input:
```
150
12
100
```
Output:
```
Litres: 12.50
Cost: 1250.00
```

There are at least five bugs. Find them all. The tests explain what each one causes.
