## Hint 1

What does `isinstance(value, int)` say about `True`? Which check do you have to do **first** to reject booleans? And what must come before the range check: the type check, or the value check? (Compare `"21" < 0`.)

## Hint 2

For `require_str_list`, first test the container with `isinstance(values, list)`. Then test every item with a loop (or `all(...)`). Return the same list at the end.

## Hint 3

```
def set_age(age):
    if isinstance(age, bool) or not isinstance(age, int): raise TypeError("age must be an int")
    if age < 0 or age > 150: raise ValueError("age must be between 0 and 150")
    return age

def require_str_list(values):
    if not isinstance(values, list): raise TypeError("expected a list")
    for item in values:
        if not isinstance(item, str): raise TypeError("every item must be a str")
    return values
```
