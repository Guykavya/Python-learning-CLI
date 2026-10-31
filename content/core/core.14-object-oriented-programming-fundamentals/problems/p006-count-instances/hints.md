## Hint 1

`self.count += 1` looks right, but it means `self.count = self.count + 1`. Where does an
assignment through `self` store the value: in the class or in the object? Which name always means
the class itself?

## Hint 2

Inside `__init__`, write to the class through its name (`Ticket.count`) or through `type(self)`.
Inside a classmethod, the first parameter `cls` **is** the class, so `cls.count = 0` changes the
class attribute.

## Hint 3

```
class Ticket:
    count = 0

    def __init__(self, title):
        self.title = title
        Ticket.count += 1          # change the class attribute
        self.number = Ticket.count # copy the value into this ticket

    @classmethod
    def reset(cls):
        cls.count = 0

    @classmethod
    def how_many(cls):
        return cls.count
```
