## Hint 1

Ignore the deadline first. Layer A tries B `attempts[0]` times; **each** of those tries makes B try C `attempts[1]` times; **each** of those makes C try the database `attempts[2]` times. How do the counts of nested loops combine, and how long does each database call take?

## Hint 2

The deadline is checked **before every attempt at every level**: once the clock has reached it, the layer returns failure without trying. The clock only moves when the database is called. So how many database calls fit in 10 seconds, if each takes exactly 1?
