## Approach

There is one counter for all tickets, so it lives in the class body as a class attribute
(chapter section 5). Each ticket's number is different, so it is an instance attribute.

The trap is `self.count += 1`. It reads `count` from the class (0), then **assigns** `self.count = 1`
on the new object. The class counter never moves, and every ticket gets number 1. To change the class
attribute, assign through the class: `Ticket.count += 1`.

`reset` and `how_many` work on the class, not on one ticket, so they are classmethods (section 6).
Python passes the class as `cls`, even when you call them on an instance.

## Code

```python
class Ticket:
    count = 0

    def __init__(self, title):
        self.title = title
        Ticket.count += 1
        self.number = Ticket.count

    @classmethod
    def reset(cls):
        cls.count = 0

    @classmethod
    def how_many(cls):
        return cls.count
```

## Complexity

O(1) for creating a ticket and for both classmethods.

## Another way

`type(self).count += 1` also writes to the class, and it is the class of *this* object. That matters
if a subclass, say `UrgentTicket(Ticket)`, should have its own counter: the first `type(self).count += 1`
reads the inherited `Ticket.count` and then creates `UrgentTicket.count`, a separate counter from
then on (give `UrgentTicket` its own `count = 0` to start it at zero). With `Ticket.count += 1`,
all kinds of tickets share one counter. Pick the one your design wants. The standard library's
`itertools.count(1)` is another way to hand out numbers: `number = next(counter)`.
