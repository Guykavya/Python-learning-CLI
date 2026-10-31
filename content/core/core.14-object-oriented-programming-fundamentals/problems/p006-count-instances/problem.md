# Numbered tickets with a class counter

A help desk gives every new ticket the next number: 1, 2, 3, ... The counter belongs to the
**class** (there is one counter for all tickets), but each number belongs to one **ticket**.

Write a class `Ticket` in `solution.py`:

- A class attribute `count`, starting at `0`. It always holds how many tickets were made so far.
- `Ticket(title)` stores `title`, adds 1 to the class counter, and gives the new ticket an instance
  attribute `number` equal to the new counter value.
- A **classmethod** `reset()` sets the class counter back to `0`, so the next ticket is number 1.
- A **classmethod** `how_many()` returns the class counter.

**Example**

```python
a = Ticket("Printer jam")
b = Ticket("No wifi")
print(a.number, b.number)        # 1 2
print(Ticket.count)              # 2
print(Ticket.how_many())         # 2
Ticket.reset()
c = Ticket("Broken chair")
print(c.number, Ticket.count)    # 1 1
print(a.number)                  # 1   (old tickets keep their numbers)
```
