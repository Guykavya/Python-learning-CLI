## Hint 1

Ask: which exact values mean "missing" here? Only `None`. So which test asks "is this the
`None` object" and nothing else? And for `True` / `False`: what does `1 == True` give? What
about `1 is True`?

## Hint 2

Each helper needs one precise question instead of the vague truthiness shortcut.

```
describe:       is None -> "missing"; is True -> "yes"; is False -> "no";
                then == 0, == "", == [] ; otherwise "value " + repr
first_non_empty: for v in values: if v is not None: return v ; return default
config_get:      value = config.get(key); return default if value is None else value
```
Put the `is True` / `is False` checks **before** the `== 0` check. Why? (`False == 0`.)
