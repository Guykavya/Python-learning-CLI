## Hint 1

Think about the JSON types: object, array, string, number, true, false, null. Which Python type becomes which? What happens to a key that is an int, and to a tuple?

## Hint 2

JSON object keys are always strings. A tuple becomes an array, and an array comes back as a list. `True` becomes `true`, `None` becomes `null`. `ensure_ascii=True` (the default) writes non-ASCII characters as `\uXXXX`.
