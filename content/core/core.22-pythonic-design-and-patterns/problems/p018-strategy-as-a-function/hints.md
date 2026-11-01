## Hint 1

What does `checkout` need from "the discount"? Only one thing: a way to turn a total into a
new total. What Python object does exactly that and can be passed as an argument?
`percent_off(10)` must remember the number 10. Which feature lets a function remember a value
from the function that created it?

## Hint 2

```
def percent_off(p):
    define inner(total): return total minus p percent of total
    return inner            # no brackets: return the function itself

def flat_off(n):
    define inner(total): return max(total - n, 0)
    return inner

def checkout(items, strategy=no_discount):
    return round(strategy(sum(items)), 2)
```
