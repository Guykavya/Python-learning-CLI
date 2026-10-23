## Approach

Check the shape first (exactly two parts), then convert, then check the range. Translating the `int` error into your own message with `from None` (chapter 7) gives the caller one clear exception type and message per mistake. The minute check includes the lower side, so `"1:-5"` is also rejected.

## Code

```python
def parse_time(text):
    parts = text.strip().split(":")
    if len(parts) != 2:
        raise ValueError("expected H:MM, like 1:30")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError:
        raise ValueError("hours and minutes must be whole numbers") from None
    if minutes < 0 or minutes > 59:
        raise ValueError("minutes must be 0 to 59")
    return hours * 60 + minutes
```

## Complexity

O(n) in the length of the text.

## Another way

Unpack with `hours_text, minutes_text = parts` after the length check, and convert each in its own `try` so the message can say which part is wrong.
