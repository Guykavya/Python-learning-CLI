## Hint 1

Name lookups need a dict from name to phone. What do you need so that "who owns this phone?"
is also O(1)?

## Hint 2

Keep **two** dicts in step: `by_name` (name to phone) and `by_phone` (phone to name). Every
`add`, `update` and `delete` must change both. On `update`, remove the old phone from
`by_phone` before adding the new one.

## Hint 3

Use `match parts:` with cases such as `case ["add", name, phone]:` and a final `case _:`.
For `find`, filter with `name.lower().startswith(prefix.lower())` and sort with `key=str.lower`.
