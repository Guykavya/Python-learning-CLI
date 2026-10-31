## Hint 1

With a normal `raise`, the function stops at the first problem. How can you remember a problem and
keep going? You can create an exception object **without** raising it: `err = ValueError("...")` is
just an object you can put in a list.

## Hint 2

For each field: first "is the key missing?" (`field not in data`). Only if it is present, check its
value. Use `if/elif` so each field adds at most one error. For `age`, check the type before the range;
`"19" < 0` would crash with a `TypeError` of its own.

## Hint 3

```
def validate_user(data):
    errors = []
    if "name" not in data:            errors.append(KeyError("name"))
    elif data["name"].strip() == "":   errors.append(ValueError("name must not be empty"))
    if "email" not in data:           errors.append(KeyError("email"))
    elif "@" not in data["email"]:     errors.append(ValueError("email must contain @"))
    if "age" not in data:             errors.append(KeyError("age"))
    elif not isinstance(data["age"], int): errors.append(TypeError(...))
    elif not 0 <= data["age"] <= 150:  errors.append(ValueError(...))
    if errors:
        raise ExceptionGroup("invalid user", errors)
    return None
```
