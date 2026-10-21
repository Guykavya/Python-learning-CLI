**1. Why.** Each lambda is a **closure**: it refers to the name `label`, which is not defined
inside the lambda. It does not store the string `label` held when the lambda was created; it
stores a way to find the **variable** (at module level, the global `label`; inside a function, a
**cell** shared by every closure created in that scope). There is only **one** `label` variable,
and the loop rebinds it to `"Save"`, then `"Open"`, then `"Quit"`. The lambdas look `label` up
only when they are **called** (that is **late binding**). They are called after the loop has
finished, when `label` is `"Quit"`, so all three return `clicked Quit`.

**2. Not lambda's fault.** The same happens with

```python
for label in ["Save", "Open", "Quit"]:
    def act():
        return "clicked " + label
    actions.append(act)
```

`def` creates a closure over the same single variable, so the result is identical.

**3. Fixes.**

Default argument:

```python
actions.append(lambda label=label: "clicked " + label)
```

Default values are evaluated once, **when the function is created**. So each lambda gets its own
parameter `label` whose default is the value the loop variable had at that moment. Inside the
lambda, `label` now means the parameter (a local), not the shared loop variable.

Factory function:

```python
def make_action(text):
    return lambda: "clicked " + text

for label in ["Save", "Open", "Quit"]:
    actions.append(make_action(label))
```

Each call of `make_action` creates a **new scope** with its own variable (cell) `text`, holding
the value passed in. Each returned lambda closes over a different cell, and nothing ever rebinds
those cells, so each keeps its own label.

**4. Comparison.** The default-argument fix changes the function's signature: a caller can
accidentally pass an argument (`act("oops")`) and override the captured value, and readers often
find `label=label` puzzling. The factory makes the intent explicit and keeps the signature clean,
at the cost of a few more lines.

**5. When late binding helps.** A closure that reads a setting, such as
`lambda: "volume " + str(volume)` where `volume` can change later, always reports the **current**
value instead of a stale copy. The same rule that causes the trap also makes such "live" closures
possible.

Key ideas to check: closures capture variables not values; one shared variable; lookup at call
time; defaults evaluated at definition time; each factory call makes a new cell; the signature
drawback of `label=label`.
