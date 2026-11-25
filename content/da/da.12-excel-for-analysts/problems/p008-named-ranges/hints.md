## Hint 1

`DefinedName(name, attr_text="Orders!$D$2:$D$6")` is the definition; `wb.defined_names[name] = definition` stores it (and replaces an older one of the same name). How do you build the text from the sheet name, the column and the last row?

## Hint 2

```text
for name, col in (("Region","B"), ("Cat","C"), ("Rev","D")):
    wb.defined_names[name] = DefinedName(name, attr_text=f"{sheet}!${col}$2:${col}${n_rows + 1}")
```
