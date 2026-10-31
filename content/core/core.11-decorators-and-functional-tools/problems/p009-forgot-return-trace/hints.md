## Hint 1

`@trace` means `add = trace(add)`. What does `trace` return if it has no `return` statement?
What happens when you put `(2, 3)` after that value?

## Hint 2

In `quiet`, the decorator returns the wrapper, so `mul` is a real function. But what does the wrapper
itself return? A function without `return` gives back `None`. Also: the wrapper has no `functools.wraps`.
The error text for calling `None` is `'NoneType' object is not callable`.
