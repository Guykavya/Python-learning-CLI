## Hint 1

Keep two boxes on paper: **`vars(g)`** (what the instance owns) and **`Gadget`** (what the class
owns), plus `vars(h)`. Update them on every assignment or `del`. For each read, look in the instance
box first, then the class box, except for `price`: a property on the class always wins.

`g.tags.append("new")` does not assign to `g.tags`. Which box does the list live in? And
`h.tags = [...]`?

## Hint 2

```text
after __init__:  vars(g) = {name: pen, _price: 100}   vars(h) = {name: cup, _price: 100}
g.color = "red"  -> vars(g) gets color
del g.color      -> vars(g) loses color again
g.__dict__["price"] = 5 -> vars(g) has price, but g.price still calls the property
```

Two lines print `getter runs`. One is inside `print("price is", g.price)`. Where does the other one
come from? Look at the last line very carefully.
