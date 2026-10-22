## Hint 1

Which dict method returns `None` for a missing key instead of raising `KeyError`? What type does that make the result?

## Hint 2

In `greeting` and `shout_name`, the value from `find_user` might be `None`. What would happen with `name.upper()` if it is? Which check makes it safe: `if name is None` or `if not name`? Think about the user `"u3"`.

## Hint 3

```
def find_user(users, user_id): return users.get(user_id)

def greeting(users, user_id):
    name = find_user(users, user_id)
    if name is None: return "Hello, guest!"
    return "Hello, " + name + "!"

def shout_name(users, user_id):
    name = find_user(users, user_id)
    if name is None: return None
    return name.upper()
```
