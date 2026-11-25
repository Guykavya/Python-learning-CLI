# Calculated column or measure?

Chapter section 5.1. A **calculated column** is computed **row by row when the data are loaded** and stored in the table (it has a **row context**). A **measure** is computed **when a visual asks for it**, in the **filter context** of that visual, and stores nothing.

In `answer.md`, for each of these six needs say **calculated column or measure**, and give a one-sentence reason (stored or computed at query time, row or filter context). About 250 to 350 words.

1. a **price band** (`Low`, `Medium`, `High`) for each product, used as a slicer;
2. the **margin %** of the whole report (it must change with every slicer);
3. a **running total** of revenue by date;
4. the **age group** of each customer, used on an axis;
5. the number of **distinct customers** who bought;
6. **revenue per store**, shown in a table with one row per store.

## Example

"A price band is a property of one product, it does not change with slicers and it is used to **slice**, so it is a calculated column (or better, a column made in Power Query)."
