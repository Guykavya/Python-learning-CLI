## Hint 1

Do the questions one at a time, and run each on its own in a scratch script first, printing the rows. Which questions need a join, which need `GROUP BY`, which need a window function? Q5 and Q9 are the traps: for Q5, where does the status filter belong so that customers without orders still appear? For Q9, what is the "unit" you average (an order, or an item row)?

## Hint 2

```
Q1-Q4: WHERE / GROUP BY / IS NULL / anti-join (LEFT JOIN ... WHERE right.key IS NULL)
Q5:    customers LEFT JOIN orders ON ... AND status <> 'cancelled' LEFT JOIN order_items ... GROUP BY customer, COALESCE(SUM(...), 0)
Q6:    orders JOIN order_items WHERE status <> 'cancelled' GROUP BY strftime('%Y-%m', ordered)
Q7:    SUM(qty) per book ... ORDER BY units DESC, title LIMIT 3
Q8:    COUNT(DISTINCT month) ... HAVING
Q9:    WITH totals AS (SUM per order) SELECT city, AVG(total) ... GROUP BY city
Q10:   ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) in a subquery, keep 1
Q11:   Q6 as a CTE + SUM(revenue) OVER (ORDER BY month)
Q12:   revenue per author, RANK() OVER (ORDER BY revenue DESC)
```

Check each question's row count against common sense: 12 customers in Q5, 3 rows in Q7, 5 authors with sales in Q12.
