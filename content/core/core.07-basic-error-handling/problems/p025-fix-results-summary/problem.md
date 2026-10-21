# Fix the results summary

A classmate wrote two functions to summarise test results typed as lines like `"Asha,82"`. They
proudly say "it never crashes". It also never works properly. `starter.py` contains their code.
**Find and fix the bugs** so both functions match their descriptions.

1. `parse_result(line)` returns `(name, marks)` with the name stripped and the marks an int. For a
   bad line it raises `ValueError` with the message for the **actual** problem:
   - not exactly two comma-separated fields: `expected 'name,marks', got <line!r>`
   - marks not a whole number: `marks must be a whole number, got <marks text stripped, !r>`
   - marks outside 0 to 100: `marks must be from 0 to 100, got <marks>`

   If `line` is not a string at all, that is a programming bug: it must **not** be turned into a
   `ValueError` (let whatever Python raises propagate).
2. `summarise(lines)` returns `(average, errors)`: the average of the valid marks (or `None` when
   there are none) and a list of `"line <n>: <message>"` strings, numbered from 1, one for each
   bad line.

**What the classmate sees**

```python
summarise(["Asha,82", "Ravi,78"])
# (None, [])                   <- should be (80.0, [])
summarise(["Asha,82", "Meena,75,80", "Ravi,eighty"])
# (None, [])                   <- should be (82.0, ["line 2: expected 'name,marks', got 'Meena,75,80'",
#                                                   "line 3: marks must be a whole number, got 'eighty'"])
```

There are three separate problems. Two are hidden by over-wide exception handling; the third is
a `try` block so wide that its message lies. Fix them without adding any bare `except:` or
`except Exception`.
