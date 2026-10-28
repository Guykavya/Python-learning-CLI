- Storing `self.total` in `__init__` and updating it in `add_line`. Then setting `discount_percent`
  forgets to update it, and the total is wrong.
- In the setter, assigning `self.discount_percent = value`. That calls the setter again, forever.
  Store into `self._discount_percent`.
- `apply_coupon` writing `self._discount_percent = ...` directly. It skips the setter's checks,
  including the "already placed" check.
- Checking free shipping on the subtotal instead of `subtotal - discount`.
- Charging shipping for an empty order.
- Using `>` instead of `>=` for the free-shipping limit: an order of exactly 500 should ship free.
- Forgetting `_check_open()` in one of the changing methods, so a placed order can still change.
