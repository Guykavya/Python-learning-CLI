## Approach

`os.environ` holds the environment variables the shell passed to this process.
`.get(name, default)` reads one safely.

## Code

```python
import os

name = os.environ.get("LEARNER_NAME", "stranger")
level = os.environ.get("LEARNER_LEVEL", "beginner")
print("Hello, " + name + "!")
print("Level: " + level)
```

## Why `.get` and not `[...]`

`os.environ["LEARNER_NAME"]` raises `KeyError` when the variable is missing,
and the program crashes. `.get` returns the default instead.

## How the shell passes values

`LEARNER_NAME=Asha python3 solution.py` sets the variable for that one command.
`export LEARNER_NAME=Asha` sets it for every later command in that terminal.
A plain `LEARNER_NAME=Asha` on its own line (no export) is **not** passed to
child programs, so Python would see nothing.

## Another way

`print("Hello, ", name, "!", sep="")` gives the same line using `sep`.
