# Explain the late-binding trap

A student builds a menu of button actions:

```python
actions = []
for label in ["Save", "Open", "Quit"]:
    actions.append(lambda: "clicked " + label)

for act in actions:
    print(act())
```

They expect `clicked Save`, `clicked Open`, `clicked Quit`, but get `clicked Quit` three times.

In `answer.md`:

1. Explain exactly why, using the words **closure**, **variable** (or **cell**) and **late
   binding**. Say when the lambda looks up `label`.
2. Show that the problem is not caused by `lambda`: what happens with a `def` inside the loop?
3. Give **two** fixes with code: the default-argument fix and the factory-function fix. Explain
   why each works, using what you know about when default values are evaluated and about each
   function call creating a new scope.
4. Compare the two fixes: one disadvantage of the default-argument fix.
5. Describe a situation where late binding is actually what you want.
