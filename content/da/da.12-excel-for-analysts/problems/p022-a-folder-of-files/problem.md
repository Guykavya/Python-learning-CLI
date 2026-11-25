# A folder of files

Chapter section 9.5. Power Query's "Combine files" reads every file of a folder and stacks them. The same in pandas, with the traps of real folders. Power Query cannot run offline; this problem checks the numbers and the steps in pandas, not the Power Query objects.

Write `combine_folder(folder)` for a folder (a `pathlib.Path`) of `.csv` files:

- read the files in **sorted file-name order**, every value as **text** (`dtype=str`, `keep_default_na=False`);
- **skip empty files** (zero bytes) silently;
- in a file, a row that **repeats the header** (every value equals the column name; typical when exports are pasted together) is dropped;
- add a column `source` with the file name (for example `orders_01.csv`) as the **last** column;
- all files must have the same columns, in any order: if a file has different column names, raise `ValueError("columns differ in <file name>")`; a different order is fine (use the column order of the first file);
- return one DataFrame with a reset index. An empty folder (no usable file): an empty DataFrame.

## Example

`orders_01.csv` has 2 rows and `orders_02.csv` has a repeated header row and 1 data row: the result has 3 rows with `source` values `orders_01.csv`, `orders_01.csv`, `orders_02.csv`.
