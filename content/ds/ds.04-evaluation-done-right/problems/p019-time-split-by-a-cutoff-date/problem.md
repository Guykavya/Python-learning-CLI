# Time split by a cutoff date

Chapter section 7. When the model will predict the **future**, test it on the future: train on everything before a cutoff, test on everything from the cutoff on.

Write `time_split(df, date_col, cutoff)` returning `(train, test)`: two DataFrames with the rows whose `date_col` is **before** the cutoff, and the rows **on or after** it. Keep the original row order and index inside each part. `date_col` may hold numbers (day numbers) or dates (`datetime64`); `cutoff` has the same kind (a date may also be given as a string such as `"2024-03-01"`).

## Example

```text
day: 1, 5, 9, 10, 12;  time_split(df, "day", 10)  ->  train days [1, 5, 9], test days [10, 12]
```
