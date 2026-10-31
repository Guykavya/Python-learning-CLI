## Hint 1

A property has a getter and (optionally) a setter. What should the getter of a **write-only**
property do? And for `is_locked`: what happens if you define only a getter and someone writes
`u.is_locked = True`?

## Hint 2

In `__init__`, write `self.password = password`. Because `password` is a property on the class,
this assignment calls your setter, so the checks and the hashing happen there, in one place.
The setter stores the hash in a different name, `self._password_hash`. Why must it not store into
`self.password` itself?

## Hint 3

```
@property
def password(self):            raise AttributeError("password is write-only")

@password.setter
def password(self, text):
    if not a str or len < 8 or no digit or no letter: raise ValueError(...)
    self._password_hash = _hash(text)

check_password(attempt):
    if locked: return False
    if _hash(attempt) == self._password_hash: wrong = 0; return True
    wrong += 1
    if wrong >= 3: locked = True
    return False
```

Create `self._wrong = 0` and `self._locked = False` in `__init__`.
