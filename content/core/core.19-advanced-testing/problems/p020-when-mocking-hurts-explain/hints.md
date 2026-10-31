## Hint 1

Change the code under test in your head: `tax.apply(0)`, `tax.apply(999)`, an empty loop. Does the test
notice? What number does `result` depend on?

## Hint 2

What would you check if you had a **real** price list and a **real** tax rule? Work out by hand what
3 pens and 2 books should cost, and compare the function with that number.

```
repo = {"pen": 10, "book": 25}     # fake: a tiny class around a dict
tax: x -> x * 1.1 or a fake that adds 10 %
expected = (3*10 + 2*25) * 1.1
```
