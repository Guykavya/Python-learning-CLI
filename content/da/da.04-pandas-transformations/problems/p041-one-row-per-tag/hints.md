## Hint 1

`.str.split(",")` turns each text into a list. Which method gives every list item its own row? After that, which two
kinds of "tag" must you throw away before counting?

## Hint 2

```text
tags = products["tags"].str.split(",").explode().str.strip()
keep tags that are not missing and not ""
counts = tags.value_counts() -> rename_axis("tag").reset_index(name="products")
sort by products (descending), tag (ascending); reset the index
```
