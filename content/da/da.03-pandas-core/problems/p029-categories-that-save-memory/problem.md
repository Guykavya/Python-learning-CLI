# Categories that save memory

Chapter sections 10.4 and 17.2. A column with few distinct values (a city, a status) stores each value once as a
`category`, and then only a small number per row. A column with many distinct values (a name, an id) gains nothing.

Write `as_category(df, max_unique=50)` returning a copy of `df` in which every **text** column with **at most**
`max_unique` distinct values (missing values do not count as a value) has the dtype `category`. Columns with more distinct values,
and columns that are not text, keep their dtype. All values (including missing ones) stay equal, the input is unchanged.

## Example

```python
df = pd.DataFrame({"city": ["Pune", "Agra", "Pune"] * 100, "name": ["n%d" % i for i in range(300)], "qty": range(300)})
out = as_category(df, max_unique=50)
out.dtypes.astype(str).to_dict()    # {'city': 'category', 'name': 'str', 'qty': 'int64'}   (pandas 3.1.1)
```
