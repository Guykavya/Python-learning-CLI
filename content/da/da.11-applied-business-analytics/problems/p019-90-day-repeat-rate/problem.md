# 90-day repeat rate

Chapter section 4.4. A simple retention KPI: **the share of new customers who place a second order within 90 days of the first**. It must be computed only for customers who have been observable for **at least 90 days**; a customer
acquired last week has not had the chance yet, and counting them as "did not repeat" would pull the rate down for the wrong reason.

Write `repeat_rate_90d(orders, customers, asof)`. `customers` has `customer_id` and `first_order`; `orders` has `customer_id` and `order_date` (the first order is among them); `asof` is the last day of data.

- **eligible**: customers with `first_order <= asof - 90 days` (a customer acquired exactly 90 days before `asof` **is** eligible);
- **repeater**: an eligible customer whose **second** order (the second earliest order date; two orders on the same day count) is at most 90 days after `first_order` (exactly 90 days counts);
- return a dict `{"eligible": int, "repeaters": int, "rate_pct": float}`; `rate_pct = repeaters / eligible * 100`, or `NaN` when nobody is eligible.

## Example

`asof = 2024-12-31`: a customer whose first order was on 2024-10-02 is eligible (exactly 90 days), one whose first order was on 2024-10-03 is not.
