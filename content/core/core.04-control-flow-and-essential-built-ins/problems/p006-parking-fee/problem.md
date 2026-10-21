# Parking fee rules

A parking lot charges by vehicle type, hours parked and day. Read three lines:

1. the vehicle type: `bike`, `car` or `truck` (any mix of capital and small letters)
2. the number of whole hours parked (0 or more)
3. the day type: `weekday` or `weekend`

Rules:

- 0 hours: the fee is 0 for every vehicle and day.
- **bike**: 10 per hour, but never more than 50. Bikes park **free** at weekends.
- **car**: 40 for the first 2 hours (even if parked only 1 hour), then 25 for each extra hour.
- **truck**: 100 per hour.
- At weekends, cars and trucks pay an **extra 20** on top.
- Any other vehicle type: print `Unknown vehicle` and nothing else.

Print `Fee: <amount>` as a whole number.

**Examples**

| Input | Output |
|---|---|
| `car`, `5`, `weekday` | `Fee: 115` |
| `bike`, `7`, `weekday` | `Fee: 50` |
| `Truck`, `2`, `weekend` | `Fee: 220` |
| `bike`, `3`, `weekend` | `Fee: 0` |
| `bus`, `1`, `weekday` | `Unknown vehicle` |
