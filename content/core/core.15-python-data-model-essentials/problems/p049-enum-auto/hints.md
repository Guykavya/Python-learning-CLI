## Hint 1

Which part of an enum body defines members, and which defines methods? Members are the names that are assigned a value (or `auto()`). What is `list(type(self))` inside a method of the enum?

## Hint 2

`from_name`: `cls[key]` is the name lookup and raises `KeyError`; turn that into `ValueError` with `try`/`except KeyError`. For `next`, the position of a member in `list(type(self))` plus one, modulo the number of members, gives the following member. For `opposite`, a small dict from member to member works.

## Hint 3

```
class Weekday(Enum): MON = auto() ... SUN = auto()
    @property is_weekend: return self in (Weekday.SAT, Weekday.SUN)
    @classmethod from_name(cls, text): key = text.strip().upper()[:3] ; return cls[key]  (KeyError -> ValueError)
    next(self): members = list(type(self)) ; return members[(members.index(self) + 1) % len(members)]
```
