## Hint 1

`update` and `combine_first` match cells by **index label and column name**. What should the index of both tables be
so that a fix lands on the right customer? Which of the two tools ignores missing values in the patch and never adds
new rows?

## Hint 2

```text
base  = old.set_index("customer_id")      (a new frame; old is untouched)
patch = fixes.set_index("customer_id")
base.update(patch)                          (in place on base; NaN in patch is ignored; unknown ids ignored)
return base.reset_index()  with the columns in old's order
```
