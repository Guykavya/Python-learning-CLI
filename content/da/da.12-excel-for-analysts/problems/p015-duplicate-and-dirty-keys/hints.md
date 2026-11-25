## Hint 1

Build the list of normalised keys first (skipping `None` and empty ones) and count them. For the other three lists, which version of each key do you look at: the original or the normalised one?

## Hint 2

```text
norm = str(k).strip().upper(); duplicates = those with count > 1
with_spaces: isinstance(k, str) and k != k.strip()
case_variants: group the stripped originals by norm; more than one distinct spelling
numbers_as_text: isinstance(k, str) and k.strip().isdigit()
```
