# Fix: four descriptor bugs

`starter.py` is a small module that a teammate wrote for validated model classes:

- `Field(kind, default=...)`: a typed attribute (`TypeError` for a wrong type), optional default.
- `Alias("price")`: a second name for another attribute (reads and writes go to `price`).
- `Model`: a base class. `Product(name="pen", price=1.5, colour="blue")` sets the fields;
  keywords that are not fields (here `colour`) go into a dict `extras` and can be read as
  attributes (`p.colour`), thanks to `__getattr__`.

It passed the teammate's one-object demo. Then four bug reports came in:

1. *"I made two products and both have the name of the second one."*
2. *"The error says `field must be float, got int`. Which field?"*
3. *"Reading `Product.cost` on the class (not on a product) crashes with an error about `NoneType`."*
4. *"`copy.copy(product)` dies with `RecursionError`."*

Copy `starter.py` to `solution.py` and fix all four. Each report has one cause in the code;
find it by reproducing the report first, then reading the method involved. Keep the design
(the same three classes, still descriptors, the same `extras` behaviour).

The intended behaviour, which the tests check:

- Every instance has its own field values; two fields in one object never share a value.
- An unset field returns its default if it has one, otherwise raises `AttributeError`.
- Error messages name the attribute, e.g. `price must be float, got int`. `Product.price.name`
  is `"price"`.
- Reading a descriptor on the class (`Product.price`, `Product.cost`) returns the descriptor itself.
- Reading a missing name raises `AttributeError` (never `RecursionError` or `KeyError`), also on
  an object whose `__init__` never ran (that is how `copy` and `pickle` build objects).

**Example**

```python
a = Product(name="pen", price=1.5)
b = Product(name="ink", price=9.0)
a.name                      # starter: 'ink'   fixed: 'pen'
Product(name=3)             # starter: TypeError: field must be str, got int
                            # fixed:   TypeError: name must be str, got int
Product.cost                # starter: AttributeError: 'NoneType' object has no attribute 'price'
                            # fixed:   <solution.Alias object at 0x...>  (address differs)
copy.copy(a)                # starter: RecursionError   fixed: a working copy
```
