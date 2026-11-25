# The retention matrix

Chapter section 4.2. A **cohort** is the group of customers whose first order was in the same month. The **retention matrix** answers: of the customers of each cohort, what share ordered again in month `k` after their first
month (`k = 0` is the cohort month itself, so `k = 0` is always 1.0)?

Write `retention_matrix(orders, customers, asof)`. `orders` has `customer_id` and `order_date`; `customers` has `customer_id` and `first_order`; `asof` is a timestamp, the last day of data.

- rows: the cohort month (`Period` of freq `M`) of every customer, sorted; columns: `0, 1, 2, ...` up to the largest number of months that any cohort has been observed;
- cell `(cohort, k)`: the number of **distinct** customers of the cohort with at least one order in the month `cohort + k`, divided by the cohort size (a proportion, not a percent);
- orders after `asof` are ignored;
- **the trap**: a cell that has **not happened yet** (the month `cohort + k` is after the month of `asof`) is **`NaN`**, not 0. A cell that has happened with no active customer is **0.0**.

## Example

Cohort 2024-01 (2 customers) with `asof` in March 2024 has cells for k = 0, 1, 2. Cohort 2024-03 has only k = 0; its k = 1 and k = 2 are `NaN`.
