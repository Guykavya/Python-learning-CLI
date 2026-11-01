## Approach

A descriptor's methods receive the instance as an argument, so all per-object data comes from
`instance`, and the descriptor keeps only configuration (here the `source` name). `Upper` has
only `__get__`, which makes it a non-data descriptor; `Fahrenheit` also has `__set__`, which makes
it a data descriptor, so `t.fahrenheit = 50` runs `__set__` instead of writing into `vars(t)`.

## Code

```python
class Upper:
    def __init__(self, source):
        self.source = source

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.source).upper()


class Fahrenheit:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.celsius * 9 / 5 + 32

    def __set__(self, instance, value):
        instance.celsius = (value - 32) * 5 / 9
```

## Complexity

O(1) per read or write (plus O(len) for `.upper()`).

## Another way

`property` is a ready-made data descriptor, so for one class you would just write:

```python
class Temperature:
    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9
```

A descriptor class pays off when the same behaviour is needed in many classes or many
attributes (`Upper("name")`, `Upper("city")`): the logic is written once and configured per use.
