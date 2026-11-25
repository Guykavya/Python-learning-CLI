# Fix the broken model

Chapter section 8. A model can pass every "does it load?" check and still give wrong numbers. Three tests find the three kinds of fault: the **value test** (a grid of contexts against pandas), the **reachability test** (does every measure change when you slice by every dimension it should?) and the **structure lint** (keys, orphans, both-way filters, date gaps). Power BI cannot run offline; the checker evaluates your DAX with MiniDAX, the small DAX engine of the chapter, and compares every number with pandas.

`starter.py` has `build_model(Model, tables)` (`Model` is the engine class, `tables` a dict with `Date`, `Product`, `Customer`, `Store`, `Sales`, `Orders`). It contains **three faults**:

1. a relationship is **missing** (a slicer on a dimension has no effect on the sales);
2. the `Revenue` measure has an `ALL(Product)` **left in** (a product slicer is ignored);
3. the `Revenue` measure **forgets the discount**.

Fix the function, **without changing its signature or the names of the measures** (`Revenue`, `Quantity`, `Orders`, `Customers`, `Cost`, `Margin`, `Margin %`, `Freight`). `Revenue` is the sum over the lines of quantity x unit price x (1 - discount). After the fix, the three tests pass: every measure equals pandas on a grid of contexts, every measure changes when sliced by the dimensions it can reach, and the structural lint finds nothing.

## Example

With the Sales-Store relationship missing, `Revenue` for `Store[Region] = North` equals the total revenue: the region filter never reaches the sales.
