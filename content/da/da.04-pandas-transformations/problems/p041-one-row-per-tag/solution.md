## Approach

Split, explode, clean, count. `explode` is a deliberate fan-out: one row per list item. An empty text splits into
`[""]` and a trailing comma leaves a `""` item, so after stripping, drop empty strings; a missing `tags` value stays
missing through `split` and `explode`, so drop missing values too. `value_counts` counts, and an explicit sort fixes
the order of ties.

## Code

```python
import pandas as pd


def tag_counts(products):
    tags = products["tags"].str.split(",").explode().str.strip()
    tags = tags[tags.notna() & (tags != "")]
    out = tags.value_counts().rename_axis("tag").reset_index(name="products")
    return out.sort_values(["products", "tag"], ascending=[False, True]).reset_index(drop=True)
```

## Complexity

O(total number of tags) for split, explode and count, plus sorting the distinct tags.

## Another way

`products.assign(tag=products["tags"].str.split(",")).explode("tag")` keeps `product_id` next to each tag, which
lets you count **distinct** products per tag with `groupby("tag")["product_id"].nunique()` (safer if a product could
list the same tag twice).
