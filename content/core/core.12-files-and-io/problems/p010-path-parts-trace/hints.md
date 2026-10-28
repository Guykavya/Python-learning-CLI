## Hint 1

`name` is the last part. `suffix` is only the last dot and what follows; `stem` is the name without it. What does `/` do when the right side starts with `/`?

## Hint 2

`with_suffix` replaces only the last suffix, so `sales.2024.csv` becomes `sales.2024.json`. `with_stem` replaces the part before the last suffix. `parts` is a tuple of strings. `..` is not resolved by pure paths.
