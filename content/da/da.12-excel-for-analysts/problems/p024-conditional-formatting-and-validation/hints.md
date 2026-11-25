## Hint 1

`ws.conditional_formatting.add(range, rule)` takes a rule made with `CellIsRule(operator=..., formula=[...], font=..., fill=...)`. A `DataValidation` is created, added to the sheet with `ws.add_data_validation(dv)` and then applied to cells with `dv.add("H1")`.

## Hint 2

```text
rule = CellIsRule(operator="lessThan", formula=[str(target)], font=Font(color="C00000", bold=True), fill=PatternFill("solid", start_color="F4B183"))
dv = DataValidation(type="list", formula1='"' + ",".join(regions) + '"', allow_blank=False, showErrorMessage=True, error="Pick a region from the list")
```
