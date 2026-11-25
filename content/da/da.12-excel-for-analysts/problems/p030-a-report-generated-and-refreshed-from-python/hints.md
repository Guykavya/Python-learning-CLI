## Hint 1

Build the pieces in the order of the statement and check each one: the Products sheet and the lookup columns first (compare one row with pandas), then the names, then the Summary. Run the verification after each step so you know which step broke it.

## Hint 2

```text
wb = Workbook(); Summary = wb.active; wb.create_sheet("Orders"), ("Products"), ("Inputs")
Orders: header + raw values + five formulas per row (k from len(products))
names: for name, col in ...: wb.defined_names[name] = DefinedName(name, attr_text=f"Orders!${col}$2:${col}${n+1}")
Summary: KPIs, the grid with mixed references, a CellIsRule on B6; fullCalcOnLoad
```
