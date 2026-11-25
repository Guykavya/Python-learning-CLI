# Five problems of one big table

Chapter section 2.2. BrightMart, a home-goods retailer, receives one big **flat export**: one row per order line, with the product, customer and store attributes repeated on every row, and the **freight** of the whole order repeated on every line of the order.

In `answer.md`, name **five problems** of working from this flat table and give a **BrightMart example** for each. About 250 to 350 words. Cover at least:

1. repeated attributes (the same text stored thousands of times);
2. an **update anomaly** (a category is renamed);
3. an **ambiguous grain** (what does one row mean?);
4. **double counting** of an order-level value (freight);
5. size and speed, and charts with missing weeks.

## Example

A start: "Repeated attributes: the product name, category and brand of Product 07 appear on every one of the roughly 400 order lines that mention it, so..."
