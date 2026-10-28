# Trace: class attributes and instance attributes

A name written directly in the class body (`team = "red"`) is a **class attribute**: one value,
stored once, in the class. A name set with `self.name = ...` is an **instance attribute**: stored in
that one object. Read the program and work out what it prints.

```python
class Player:
    team = "red"
    lives = 3
    badges = []

    def __init__(self, name):
        self.name = name

    def lose_life(self):
        self.lives -= 1

    def earn(self, badge):
        self.badges.append(badge)


p = Player("Asha")
q = Player("Ben")
print(p.team, q.team)

p.team = "blue"
print(p.team, q.team, Player.team)

Player.team = "green"
print(p.team, q.team)

p.lose_life()
print(p.lives, q.lives, Player.lives)
print("lives" in vars(p), "lives" in vars(q))

q.earn("gold")
print(p.badges, len(Player.badges))

p.badges = ["silver"]
p.earn("bronze")
print(p.badges, q.badges)

del p.team
print(p.team)
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- **Reading** `obj.attr` looks in the object first (`vars(obj)`, its own dict). Only if the name is
  not there, Python looks in the class.
- **Assigning** `obj.attr = value` always creates or changes the attribute **in the object**.
  It never changes the class.
- `self.lives -= 1` is short for `self.lives = self.lives - 1`: one read, then one assignment.
- `self.badges.append(x)` is a read (find the list) and then a change to that list. There is no
  assignment to `self.badges`.
- `vars(obj)` is the dict of the object's own attributes. `del obj.attr` removes an attribute from
  the object.
- A list prints like `['a', 'b']`.

## Example of the format

```python
class C:
    size = 1

c = C()
c.size = 5
print(c.size, C.size)
```

prints

```text
5 1
```
