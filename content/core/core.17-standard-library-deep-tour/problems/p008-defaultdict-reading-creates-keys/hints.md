## Hint 1

Sort every read into one of two groups. **Creates the key**: `d[key]` (also inside `d[key] += 1`, `if d[key] > 0`, `d[key].append(...)`). **Does not create**: `key in d`, `d.get(key)`, `len(d)`, iterating. Go line by line and keep a small table of the dict's contents.

## Hint 2

`dict(counts)` is a plain copy: its `.get` cannot create anything. Setting `default_factory = None` turns the defaultdict back into a dict that raises `KeyError`. In the last loop, the **first** pass reads `seen["a!"]`: what happens to the dict's size, and when does the loop notice?

## Hint 3

```
stock: {apple:3}                       -> 1 {...}
stock["pear"] read -> creates pear:0   -> 2 {...}
in / get do not create                 -> False None 2
groups["c"] creates c:[]               -> [] 3
counts["y"], counts["z"] create 0s     -> total 1, keys x y z
seen loop: k="a", reads "a!" -> created; next step of the loop -> RuntimeError
```
