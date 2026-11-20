## Hint 1

Which table has the money? What do you need to put together before you can add it up per customer?

## Hint 2

`select(Customer.name, func.count(Order.id), func.sum(Order.total_paise)).join(Order, ...)`. An aggregate over a join needs a `group_by` on the customer. Sorting by the aggregate: `func.sum(...).desc()`.

## Hint 3

```text
select(Customer.name, count(Order.id), sum(Order.total_paise))
  .join(Order, Order.customer_id == Customer.id)
  .group_by(Customer.id, Customer.name)
  .order_by(sum(...).desc(), Customer.name)
  .limit(n)
```
