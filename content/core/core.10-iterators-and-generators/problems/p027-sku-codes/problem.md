# Product codes for every size and colour

A small clothes shop gives every variant of a product its own stock code (SKU), like
`TEE-M-RED`. You must make the codes for every size and colour, except the variants the
supplier does not make.

Write a **generator function** `sku_codes(product, sizes, colours, unavailable=())` in
`solution.py`.

- Yield one code `PRODUCT-SIZE-COLOUR` for each size and colour, all in **upper case**.
- Order: sizes on the outside, colours on the inside (first size with every colour, then the
  next size, and so on).
- `unavailable` holds `(size, colour)` tuples, written exactly as in `sizes` and `colours`.
  Skip those.
- Use `itertools.product` instead of nested loops.

**Example**

```python
list(sku_codes("tee", ["S", "M"], ["red", "blue"]))
# ['TEE-S-RED', 'TEE-S-BLUE', 'TEE-M-RED', 'TEE-M-BLUE']

list(sku_codes("tee", ["S", "M"], ["red", "blue"], unavailable=[("M", "red")]))
# ['TEE-S-RED', 'TEE-S-BLUE', 'TEE-M-BLUE']
```
