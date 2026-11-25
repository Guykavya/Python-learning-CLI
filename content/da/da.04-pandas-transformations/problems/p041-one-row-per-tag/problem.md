# One row per tag

Chapter section 8.7. The product table has a text column `tags` with comma-separated labels such as `"eco, gift"`.
Some products have no tags (`""` or missing), some lists have stray spaces or a trailing comma.

Write `tag_counts(products)` that returns a frame with the columns `tag` and `products`: how many products carry each
tag.

- split each `tags` text at commas and strip the spaces around every tag;
- ignore empty tags (from `""`, from `"toys,"`) and missing `tags`;
- sort by `products` from most to fewest, ties by `tag` alphabetically; fresh index `0, 1, ...`;
- do not change the input.

## Example

```python
import pandas as pd

products = pd.DataFrame({"product_id": ["P1", "P2", "P3", "P4"],
                         "tags": ["eco, gift", "gift", "", None]})
print(tag_counts(products).values.tolist())
```
```text
[['gift', 2], ['eco', 1]]
```
