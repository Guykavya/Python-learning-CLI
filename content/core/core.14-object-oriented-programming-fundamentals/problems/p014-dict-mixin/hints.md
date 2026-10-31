## Hint 1

`vars(self)` is the object's own attribute dict, the real one. What happens to the object if you
return that dict and the caller deletes a key from it? How do you build a new dict that keeps only
some of the keys?

## Hint 2

```
class ToDictMixin:
    def to_dict(self):
        return {name: value for name, value in vars(self).items()
                if not name.startswith("_")}

class Student(ToDictMixin):
    def __init__(self, name, roll):
        self.name = name; self.roll = roll; self._notes = []
```

The mixin never mentions `Student` or `Product`; it only uses `self`.
