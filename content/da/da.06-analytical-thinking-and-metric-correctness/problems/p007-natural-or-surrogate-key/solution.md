## Approach

Contrast what is stable (an arbitrary id) with what is meaningful (the phone number). Use a key for joining, and keep the
meaningful columns under their own rule.

## Code

No code. In a test you would write `check_grain(customers, "customer_id")` and, separately, check the phone numbers
after cleaning them: `customers["phone_clean"].duplicated().sum()`.

## Complexity

Not applicable.

## Another way

Many teams add a third idea: a **business key** such as `(clean_phone, name)` used only to find duplicate people, while
every join goes through the surrogate key.
