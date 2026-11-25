# Annotated heatmap

Chapter section 4.7. A heatmap shows a number for every pair of categories as a colour. Colour alone is hard to read exactly, so we write the
**value in each cell** and add a **colour bar** as the key.

Write `heatmap(pivot)`. `pivot` is a DataFrame (rows and columns are categories, cells are numbers; some cells may be `NaN`).

- draw it with `ax.imshow` and add a colour bar (`fig.colorbar`); the figure then has **two** Axes;
- x tick labels are the column names, y tick labels the row names;
- write the value of every cell with **one decimal** (`f"{v:.1f}"`), centred in the cell: use `ax.text(j, i, ...)` for column `j`, row `i`;
- a `NaN` cell gets **no text** (and stays blank, which is what `imshow` does with `NaN`).

Return the Figure.

## Example

For a 2 x 3 table with one `NaN`, the Axes holds 5 texts, and the one at column 1, row 0 reads whatever `pivot.iloc[0, 1]` is, to one decimal.
