## Approach

Apply the lookup rule from chapter section 9 for every attribute access:

1. a **data descriptor** (a property) on the class, if there is one;
2. otherwise the instance `__dict__`;
3. otherwise the class (and its parents in MRO order), where functions become bound methods.

For assignment: a property on the class handles it (or refuses it); otherwise the value goes into the
instance `__dict__`, never into the class.

## Step by step

1. `g.color`, `h.color`: no instance attribute -> class -> `grey grey`.
2. `g.color = "red"` creates an instance attribute on `g` only; the class is unchanged ->
   `red grey grey`.
3. `Gadget.color = "blue"` changes the class. `g` still has its own `red`, `h` reads the class ->
   `red blue`.
4. `del g.color` removes `g`'s own attribute, so `g.color` falls back to the class: `blue`.
   `vars(g)` is back to `name` and `_price` -> `blue ['_price', 'name']`.
5. `g.tags.append("new")` **reads** `g.tags` (the class list) and changes that one shared list.
   `h.tags = ["own"]` **assigns**, so `h` gets its own list. -> `['new'] ['own'] ['new']`.
6. `g.__dict__["price"] = 5` puts `price` into the instance dict. But `g.price` still runs the
   property, because a data descriptor wins. The getter prints first, then the whole `print`
   line runs -> `getter runs`, then `price is 100`.
7. `vars(g)["price"]` reads the dict directly -> `5`.
8. `g.price = 7`: the property has no setter -> `AttributeError` -> `cannot set price`. (The instance
   dict key does not help.)
9. `g.label = lambda: "replaced"` puts a function in `g`'s dict. Methods are not data descriptors,
   so the instance wins, and functions in the instance are not bound -> `g.label()` is `replaced`.
   `h.label()` uses the class method; `h.color` is the class value `blue` -> `replaced cup:blue`.
10. `Gadget.label(g)` calls the class function directly with `self = g` -> `pen:blue`.
11. `del g.label`, so `g.label()` is the class method again -> `pen:blue`.
12. `Gadget.label = lambda self: ...` replaces the method on the class. Neither object has its own
    `label`, so both use the new one -> `class pen class cup`.
13. Last line: `getattr(g, "size", "no size")` gives the default. `hasattr(g, "price")` really calls
    the getter, which prints `getter runs` **before** the line is printed -> `getter runs`, then
    `no size True`.

## Output

```text
grey grey
red grey grey
red blue
blue ['_price', 'name']
['new'] ['own'] ['new']
getter runs
price is 100
5
cannot set price
replaced cup:blue
pen:blue
pen:blue
class pen class cup
getter runs
no size True
```

## Complexity

Not applicable.

## Another way

Print `vars(g)`, `vars(h)` and `{k: v for k, v in vars(Gadget).items() if not k.startswith("__")}`
after each step to see the two boxes change. To see *why* a property wins, look at
`type(vars(Gadget)["price"])`: it is `property`, which defines both "get" and "set" behaviour; a plain
function defines only "get" and therefore loses to the instance dict.
