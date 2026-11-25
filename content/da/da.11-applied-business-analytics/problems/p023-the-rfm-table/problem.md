# The RFM table

Chapter section 5.1. **RFM** describes every customer with three numbers computed **as of a date**: **R**ecency (days since the last order), **F**requency (number of orders) and **M**onetary value (total spend).

Write `rfm_table(orders, customers, asof)`. `orders` has `customer_id`, `order_date`, `amount`; `customers` has `customer_id`; `asof` is a timestamp.

- ignore orders **after** `asof` (a report as of March must not know April);
- one row per customer who is in `customers` **and** has at least one order on or before `asof`; customers with no order by `asof` are **absent**;
- columns `R` (days from the customer's last order to `asof`, an int), `F` (number of orders), `M` (sum of `amount`); index = `customer_id`, sorted.

## Example

A customer with orders on 2024-01-10 (100) and 2024-03-01 (50), as of 2024-03-31, has `R = 30`, `F = 2`, `M = 150`. An order on 2024-04-05 would be ignored.
