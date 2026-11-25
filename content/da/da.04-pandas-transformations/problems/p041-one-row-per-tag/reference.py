import pandas as pd


def tag_counts(products):
    """Columns tag, products: number of products per tag, most first, ties alphabetical."""
    tags = products["tags"].str.split(",").explode().str.strip()
    tags = tags[tags.notna() & (tags != "")]
    out = tags.value_counts().rename_axis("tag").reset_index(name="products")
    return out.sort_values(["products", "tag"], ascending=[False, True]).reset_index(drop=True)
