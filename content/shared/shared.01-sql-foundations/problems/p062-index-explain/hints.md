## Hint 1

Think of the index at the back of a book: it lists the values you look up, sorted, with page numbers. What would you do to find "customer 7" without it? What does the planner do when you wrap the column in an expression?

## Hint 2

For question 3: an index is *sorted*. If it is sorted by (customer_id, ordered), what do all rows with customer_id = 7 look like inside it, in which order do you meet them, and what does `ORDER BY ordered` then need?
For question 4: what happens to the index when you insert or delete a row, and what about a query that reads half the table anyway?
