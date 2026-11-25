# Share within the category: ALLEXCEPT

Chapter section 5.5. "What share of its **category** does each product make?" needs a denominator that keeps the category but removes the product filter. `ALL(Product)` would remove the category too (a share of all revenue); `ALLEXCEPT(Product, Product[Category])` removes every filter of the table **except** the one on the category. Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

The model has the measure `Revenue` (in the starter). Write the measure `"% of category"`:

```text
the revenue of the current context, divided by the revenue of the same context in which every Product filter
except the category is removed; blank when the denominator is blank or 0
```

Other filters (year, region, ...) must stay. MiniDAX knows: SUM, SUMX, AVERAGE, MIN, MAX, COUNT, COUNTROWS, DISTINCTCOUNT, DIVIDE, IF, ISBLANK, BLANK, COALESCE, CALCULATE, FILTER, ALL, ALLEXCEPT, REMOVEFILTERS, USERELATIONSHIP, VALUES, SELECTEDVALUE, HASONEVALUE, RELATED, VAR ... RETURN, SAMEPERIODLASTYEAR, DATESYTD, DATEADD. It has no context transition (do not call a measure inside an iterator such as SUMX(Product, [Revenue])).

## Example

A visual with rows `Product[Category]` and `Product[Product]`: each product's `% of category` is its revenue divided by the revenue of its category; within one category the shares add up to 1.
