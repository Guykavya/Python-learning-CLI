## Hint 1

`isinstance(True, int)` is `True` in Python. In which order must you test the types? How can you decide if a string "looks like a number"? (Try `float(s.strip())` inside `try`.)

## Hint 2

```text
for each cell value v below the header:
  None -> blanks; bool -> booleans; int/float -> numbers; datetime/date -> dates
  str: "" -> empty_strings; float(v.strip()) works -> text_numbers; else other_text
```
