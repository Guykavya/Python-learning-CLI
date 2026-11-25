# The LTV curve

Chapter section 4.5. **Customer value over time**: how much revenue does an average customer bring in the first month, the first two months, the first year? To compare customers fairly, every customer in the curve must have been
observed for the **whole** horizon; otherwise recent customers drag the curve down because their later months have not happened.

Write `ltv_curve(orders, customers, asof, months)`:

- the time since the first order is counted in **30-day buckets**: bucket `b` holds the orders made `30 b` to `30 b + 29` days after the customer's `first_order` (so the first order itself is in bucket 0);
- **eligible** customers: those observable for the full `months + 1` buckets, i.e. `(asof - first_order).days >= 30 * months + 29`; if there are none, raise `ValueError("no customer has a full follow-up")`;
- return a Series indexed `0, 1, ..., months`: for each `b`, the **cumulative** revenue of the eligible customers up to and including bucket `b`, divided by the **number of eligible customers** (customers with no order in a bucket count as 0).

Ignore orders of non-eligible customers and orders beyond bucket `months`.

## Example

Two eligible customers who together spend 350 in bucket 0, 70 in bucket 1 and 10 in bucket 2 give the curve `[175, 210, 215]`.
