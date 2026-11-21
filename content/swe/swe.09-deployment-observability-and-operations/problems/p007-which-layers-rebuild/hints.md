## Hint 1

For each edit, find the **earliest** step that the edit touches: the step whose text changed, or the `COPY` whose copied files changed. Everything before it is cached. What happens to the steps after it?

## Hint 2

Which files does step 4 copy? Which does step 6 copy? Does any `COPY` in this Dockerfile copy `README.md`? Count the steps from the first miss to the end, inclusive: that is the number rebuilt.

```text
app/main.py edited      -> touches COPY app ./app (step 6) -> steps 6, 7, 8, 9
requirements.txt edited -> touches COPY requirements.txt . (step 4) -> steps 4 to 9
base image tag changed  -> touches FROM (step 1) -> all 9
```
