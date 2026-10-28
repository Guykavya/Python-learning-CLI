## Hint 1

Look at the first failing test. What type of object did `parse_price("Rs 12.50")` return? Rewrite `@fallback`
without the `@`: `parse_price = fallback(parse_price)`. What is `default` now, and what does that call return?

## Hint 2

Inside `wrapper`, follow the path when nothing goes wrong. Which line produces the price, and where does the
price go after that line?

## Hint 3

The three fixes:

```
from functools import wraps
...
        @wraps(func)                          # bug: name was 'wrapper'
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)  # bug: result was thrown away
            ...
@fallback(0.0)                                # bug: factory was not called
def parse_price(text): ...
```
