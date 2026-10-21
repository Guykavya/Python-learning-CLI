## Hint 1

What does `os.environ.get("HOME")` return? What does it return for a name that
does not exist?

## Hint 2

`os.environ.get(name, default)` returns the default when the variable is
missing. Join the greeting with `+` so no space appears before `!`.

## Hint 3

```
import os
name = os.environ.get("LEARNER_NAME", "<default>")
level = os.environ.get("LEARNER_LEVEL", "<default>")
print("Hello, " + name + "!")
print("Level: " + level)
```
