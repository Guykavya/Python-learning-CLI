## Hint 1

What type is `details` inside the function? Is it the same object as the caller's `extra` dict?

## Hint 2

```
profile = {"name": name}
for key, value in details.items():
    if value is not None:
        profile[key] = value
return profile
```
