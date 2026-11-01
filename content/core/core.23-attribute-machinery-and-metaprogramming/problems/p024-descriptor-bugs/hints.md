## Hint 1

Reproduce each report in a few lines first:

```python
a = Product(name="pen"); b = Product(name="ink"); print(a.name)   # report 1
Product(name="pen", price=2)                                      # report 2
Product.cost                                                       # report 3
import copy; copy.copy(a)                                          # report 4
```

Then for each one, ask:
1. How many `Field` objects exist for `name`: one per product, or one per class? Where does `__set__` put the value?
2. Where does `self.name` get its value? Which hook would tell a descriptor its attribute name?
3. What is `instance` when you read an attribute on the **class**?
4. `copy` creates the object without `__init__`. Inside `__getattr__`, what happens when `self.extras` does not exist yet?

## Hint 2

The four fixes, as pseudocode:

```
Field.__set_name__(owner, name):  self.name = name
Field.__set__:   instance.__dict__[self.name] = value        (not self.value)
Field.__get__:   instance None -> self
                 try instance.__dict__[self.name]
                 except KeyError: default if there is one, else AttributeError
Alias.__get__:   if instance is None: return self
Model.__getattr__: extras = vars(self).get("extras", {})      (cannot call __getattr__ again)
```
