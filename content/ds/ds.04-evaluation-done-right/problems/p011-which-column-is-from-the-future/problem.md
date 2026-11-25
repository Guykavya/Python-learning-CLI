# Which column is from the future?

Chapter section 4.5. We predict churn on **day 100** for every customer. For each candidate feature, the data owner told us on which day its value is known (for a typical customer):

```python
PREDICT_DAY = 100
known_at = {
    "created_at": 10,
    "last_login": 98,
    "support_calls_30d": 99,
    "plan_change": 100,
    "refund_issued": 115,
    "cancelled_at": 130,
}
usable = []
for name, day in known_at.items():
    ok = day <= PREDICT_DAY
    print(f"{name}: {'usable' if ok else 'future'}")
    if ok:
        usable.append(name)
print(f"{len(usable)} usable of {len(known_at)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `{"signup_channel": 1}` the program would print `signup_channel: usable` and then `1 usable of 1`.

## After you answer

- `plan_change` is known exactly on day 100. Would you trust it? What would you ask the data owner?
