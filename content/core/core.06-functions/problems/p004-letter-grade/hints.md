## Hint 1

Once a `return` runs, can any later line in the function run in that call?

## Hint 2

```
if score < 0 or score > 100: return "invalid"
if score >= 90: return "A"
if score >= 75: return "B"
...
return "F"
```
Each check only runs if every check above it failed, so you only need lower bounds.
