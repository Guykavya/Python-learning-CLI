## Model answer

**What changes.** With a single direction a filter flows from the one side (a dimension) down to the many side (the fact) and stops. With **both** directions the filtered fact rows also **filter the other dimension**: in BrightMart, with `Store = Store 12` and the month `2023-01` selected, a single-direction model still lists **all 40 products**
(the store and date slicers never reach the product table), while a model with `Sales -> Product` and `Sales -> Store` set to both directions shows only the products sold in that store in that month. The product slicer now **changes by itself** when an unrelated slicer changes.

**Three dangers.**
1. **Ambiguous paths.** With several both-way relationships a filter can reach a table by more than one route (Store -> Sales -> Product -> Sales again); the engine has to pick one, and a small change to the model changes which.
2. **Leaks into unrelated dimensions.** A filter on Store ends up filtering Date, Product and Customer through the fact table, so a visual that was meant to be "all products" shows a subset.
3. **Numbers that change when a slicer is added.** A card that showed a total now shows less when someone adds a slicer for a different table, and nobody can say why without rebuilding the filter path by hand.

**Instead.** Keep every relationship **single-direction** (one to many), and answer the business question with an **explicit measure**: for example "customers who bought" = `DISTINCTCOUNT(Sales[CustomerKey])`, which is filtered by the product slicer through the fact table. Both directions is acceptable in narrow, tested cases (a many-to-many bridge table, or a slicer list that should only show members with data), and then only after the reachability test and the grid against pandas still pass.

**Checklist: your answer should mention**
- [ ] the direction of the filter flow (dimension to fact) and what "both" adds
- [ ] the 40-product example becoming smaller when slicers on other tables are used
- [ ] ambiguous paths
- [ ] leaks into unrelated dimensions / numbers changing when a slicer is added
- [ ] the safer alternative: single direction plus a measure; narrow exceptions and tests
