## Approach

Apply the two sorts in sequence and apply the tie rule of stability at the second one.

## Expected output

```text
[('eli', 35), ('dee', 25), ('cy', 30), ('bob', 25), ('ann', 30)]
[('dee', 25), ('bob', 25), ('cy', 30), ('ann', 30), ('eli', 35)]
[('eli', 35), ('dee', 25), ('cy', 30), ('bob', 25), ('ann', 30)]
True
```

## Why

Primary key = the **last** sort (age); secondary = the earlier sort (name descending). In `wrong` the primary key is the name, which is unique here, so the result is simply names descending. The final comparison is `True`, showing that two stable passes equal one pass with a tuple key. The two-pass method is what you use when the secondary key cannot be negated (strings).
