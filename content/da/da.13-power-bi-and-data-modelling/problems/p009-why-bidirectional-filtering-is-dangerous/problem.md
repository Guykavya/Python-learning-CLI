# Why bidirectional filtering is dangerous

Chapter sections 4.4 and 4.5. A colleague wants the **Customer** slicer to show only the customers who bought the product selected in the **Product** slicer. In Power BI this is a one-click change: set the relationship `Sales -> Customer` to filter **both** directions. Another colleague warns that it is a trap.

In `answer.md`, in about 250 to 350 words, explain:

1. what changes when a relationship filters in both directions (use the BrightMart example: slicers `Store = Store 12` and month `2023-01`, and the list of products);
2. the three dangers: **ambiguous paths**, filters **leaking into unrelated dimensions**, and **numbers that change when a slicer is added**;
3. what you would do instead (one-way relationships plus an explicit measure), and when both directions is acceptable.

## Example

A start: "With a single direction, a filter on Store flows down to Sales and stops there. With both directions, the filtered Sales rows also filter the products..."
