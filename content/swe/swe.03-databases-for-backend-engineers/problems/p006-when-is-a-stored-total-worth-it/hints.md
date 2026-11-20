## Hint 1

Count the work: one read of the page versus one write of a line. Who does the sum, and how often?

## Hint 2

Before, a total could not disagree with the lines, because it did not exist as a separate fact. After, there are two facts that must agree.

## Hint 3

Measures: one single piece of code that changes lines and total together, inside one transaction (or a trigger). Reconciliation: compare `orders.total_paise` with the sum computed from `order_lines` and list the rows that differ.
