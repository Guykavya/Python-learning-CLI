# Middleware and a signal

Chapter sections 16.1 and 16.2. Two hooks that run without being called by your own code: a **middleware** that wraps every request, and a **signal** receiver that reacts when a model row is saved.

The tests set Django up for you (in-memory SQLite, your `solution.py` is the app `shop`, tables are created for your models). Every model needs `class Meta: app_label = "shop"`. Do not change a model while the tests run. **Two extra settings for this problem:** the tests put `"solution.RequestIDMiddleware"` at the end of `MIDDLEWARE`, and your signal receivers must be connected when `solution.py` is imported (a `@receiver(...)` decorator at module level does that).

## Part 1: `RequestIDMiddleware`

A class with `__init__(self, get_response)` and `__call__(self, request)`. For every request:

- Take the id from the incoming header `X-Request-ID` if it is there **and valid**: 1 to 64 characters, only letters, digits, `-` and `_`. Otherwise make a new one: `uuid.uuid4().hex` (32 lower-case hex characters).
- Store it as `request.request_id` so views can use it, and send it back in the response header `X-Request-ID`. This must happen for **every** response, also for a 404.

The starter has a view `whoami` at `/whoami/` that returns `{"request_id": request.request_id}`.

## Part 2: `LowStockAlert`

`Item` has `name`, `quantity` and `threshold` (default 5). `LowStockAlert` has `item` (`ForeignKey`, `related_name="alerts"`), `quantity` (the quantity that triggered it) and `created` (`auto_now_add`).

Write a `post_save` receiver for `Item` that creates **one `LowStockAlert` each time the stock crosses the threshold downwards**: the saved quantity is `< threshold` and the quantity before this save was `>= threshold`. A brand-new item is treated as "was not low before", so creating an item below its threshold gives one alert. While the stock stays below the threshold, more saves give **no** more alerts; when it goes back to `>= threshold` and falls again, that is a new crossing. (To know the old value, a `pre_save` receiver that reads the row from the database is one way.)

## Example (threshold 5)

```text
save quantity: 10  7   4   3   4   0   5   4   9
alerts so far:  0  0   1   1   1   1   1   2   2
```
