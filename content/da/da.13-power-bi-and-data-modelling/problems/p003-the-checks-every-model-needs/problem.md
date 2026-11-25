# The checks every model needs

Chapter section 3.3. Before any report, three checks of the **keys**: a dimension key must be **unique and not blank** (otherwise a relationship cannot be built), a fact key must **not be blank**, and every fact key must **exist in its dimension** (otherwise the row is an **orphan**: it shows up as `(Blank)` in a report, or silently disappears). Power BI cannot run offline; this problem is about the model and its numbers, which we build and check in pandas.

Write `check_star(facts, dims, keys)`:

- `facts` and `dims` are dicts `{name: DataFrame}`; in a dimension the **first column** is its key;
- `keys` is a list of `(fact name, fact column, dimension name, dimension column)`;
- return a **list of strings**, in this order:
  1. for each dimension (in dict order): `"<dim>[<key>] has duplicate keys"` if its key repeats; `"<dim>[<key>] has blank keys"` if it has missing values;
  2. for each tuple of `keys` (in the given order): `"<fact>[<col>] has <n> blank keys"` if `n > 0`; then `"<fact>[<col>] has <n> orphan rows (not in <dim>[<dcol>])"` if `n > 0` (blank keys are not counted as orphans).
- a good star gives `[]`.

## Example

A fact row with `ProductKey = 99` that is not in `DimProduct` gives `FactSales[ProductKey] has 1 orphan rows (not in DimProduct[ProductKey])`.
