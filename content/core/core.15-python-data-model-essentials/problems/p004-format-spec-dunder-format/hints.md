## Hint 1

What does Python call when it sees `f"{c:hex}"`? It calls `c.__format__("hex")`. What should that method return?

## Hint 2

Compare `spec` with `if` / `elif`. For two hex digits per number use the format spec `02x`: `f"{self.r:02x}"`.

## Hint 3

```
def __format__(self, spec):
    if spec == "":     return str(self)
    if spec == "hex":  return "#" + two hex digits of r, g, b
    if spec == "rgb":  return "rgb(r, g, b)"
    raise ValueError("unknown format spec: " + spec)
```
