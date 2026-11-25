# Split a flat export into a star

Chapter section 3.2. A **star schema** has one **fact** table (one row per order line, with numbers and keys) surrounded by **dimension** tables (one row per product, customer, store, with the descriptive attributes). Power BI cannot run offline; this problem is about the model and its numbers, which we build and check in pandas.

Write `build_star(flat)`. `flat` has the columns `order_id`, `line_no`, `order_date`, `customer`, `segment`, `city`, `product`, `category`, `store`, `quantity`, `unit_price`, `discount`. Return `(fact, dims)`:

- `dims` is a dict with three DataFrames:
  - `DimProduct`: `ProductKey`, `product`, `category`;
  - `DimCustomer`: `CustomerKey`, `customer`, `segment`, `city`;
  - `DimStore`: `StoreKey`, `store`;
  each has **one row per natural key** (the product name, the customer name, the store name), the **surrogate key** is an integer `1, 2, 3, ...` assigned in **sorted order of the natural key**, and the rows are in key order;
- `fact` has one row for every row of `flat`, in the same order, with the columns `order_id`, `line_no`, `order_date`, `ProductKey`, `CustomerKey`, `StoreKey`, `quantity`, `unit_price`, `discount`;
- if one natural key has **different attributes** on different rows (for example the same customer name with two cities), raise `ValueError("conflicting attributes for <column> <value>")` (column is `product`, `customer` or `store`).

Joining the fact back to the dimensions must reproduce the revenue of the flat table exactly.

## Example

Two lines for `Product B` (category `Kitchen`) and one for `Product A` give `DimProduct` with `Product A` as key 1 and `Product B` as key 2, and a fact table with `ProductKey` `2, 2, 1`.
