## Model answer

**1. Repeated attributes.** The name, category and brand of Product 07 are stored on every order line that mentions it (about 400 lines), and the same for every customer's segment and city. The table is mostly repeated text.

**2. Update anomaly.** If the category "Kitchen" is renamed, or a product is moved to another subcategory, every one of its order lines must be changed. Miss some and the same product is in two categories in the same report. In a model with a product table there is one row to change.

**3. Ambiguous grain.** One row is "an order line", but the table also holds order-level, customer-level and product-level facts. Counting rows counts lines, not orders, customers or products, and nobody can say what a row means without asking.

**4. Double counting.** The freight of an order is repeated on each of its lines. An order with 4 lines has its freight counted 4 times when you sum the column; in BrightMart the sum is about 3 times the true freight. Freight needs its own table with one row per **order**.

**5. Size and gaps.** The wide table is several times bigger in memory than the separate tables, so the report is slower. And a chart of one product at one store from the flat table has rows only for the weeks with a sale, so the line is drawn straight across the missing weeks.

**Checklist: your answer should mention**
- [ ] repeated attributes (storage and consistency)
- [ ] the update anomaly with a concrete update
- [ ] unclear grain: what a row means
- [ ] freight double counted because it sits at order level
- [ ] size/speed and the missing weeks in charts
