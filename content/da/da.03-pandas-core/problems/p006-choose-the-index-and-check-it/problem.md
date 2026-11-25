# Choose the index, and check it

Chapter section 4.2. An index is only useful as a key when each label appears **once**. `set_index` does not check that.

Write `index_by(df, key)`:

- return a new frame whose index is the column `key` (the column leaves the data and becomes the index);
- if the values of `key` are not unique, raise `ValueError` whose message lists every duplicated key (each once);
- the input frame is not changed.

## Example

```python
df = pd.DataFrame({"sku": ["A1", "B2", "A1", "C3", "B2", "A1"], "qty": [1, 2, 3, 4, 5, 6]})
index_by(df, "sku")
# ValueError: sku has duplicated keys: ['A1', 'B2']

index_by(df.drop_duplicates("sku"), "sku").loc["B2", "qty"]   # 2
```
