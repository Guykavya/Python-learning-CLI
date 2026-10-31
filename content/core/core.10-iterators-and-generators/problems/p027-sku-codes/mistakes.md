- `from itertools import product` while the first parameter is also called `product`. Inside the
  function, `product(...)` is then the string `"tee"`, and you get `TypeError: 'str' object is not callable`.
- `product(colours, sizes)`: the codes come out in the wrong order and as `TEE-RED-S`.
- Upper-casing before checking `unavailable`, so `("M", "red")` no longer matches `("M", "RED")`.
- Returning a list: the shop may have thousands of variants; a generator gives them one by one.
