## Hint 1

What do you need to store? A dict from `user_id` to `name` is enough. Where must it be created so that
two `FakeUserRepo()` objects do not share it: in the class body or in `__init__`?

## Hint 2

Each method has one error case. Check it **before** changing the dict. For `names`, which function
gives a list ordered by key? Does `sorted(self._users)` return the keys or the names?

## Hint 3

```
__init__: self._users = {}
add(id, name): if id in users: raise DuplicateUser(id); if not name.strip(): raise ValueError; users[id] = name
get(id): if id not in users: raise UserNotFound(id); return users[id]
delete(id): same check, then del
names(): [self._users[i] for i in sorted(self._users)]
```
