## Hint 1

How do you turn 'a run of non-alphanumeric characters' into one separator? Think about a flag: did the last character start a gap?

## Hint 2

One simple way: replace every non-alphanumeric character with a space, then `split()` (which ignores runs of spaces and spaces at the ends), then `sep.join(words)`.

## Hint 3

```
cleaned = "".join(ch if ch.isalnum() else " " for ch in text.lower())
slug = sep.join(cleaned.split())
if max_length is not None:
    slug = slug[:max_length]
    while slug.endswith(sep): slug = slug[: -len(sep)]   (careful if sep is "")
return slug
```
