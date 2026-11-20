## Approach

Put every rule in the signature with `Annotated`, so FastAPI checks it before the function runs.

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/shops/{shop_id}/products")
def list_products(
    shop_id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(min_length=2, max_length=30, pattern="^[a-z0-9 ]+$")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
    tag: Annotated[list[str] | None, Query()] = None,
):
    return {"shop_id": shop_id, "q": q, "page": page, "size": size, "tags": tag or []}
```

Example: `/shops/0/products?size=51` breaks two rules, so the 422 lists two errors: `["path", "shop_id"]` with type `greater_than_equal` and `["query", "size"]` with type `less_than_equal`. The function body never runs, so it contains no `if` checks at all.

The rules on `q` apply only when `q` is sent: `None` (not sent) is allowed by the type `str | None`.

## Complexity

O(length of the query string) for parsing and checking.

## Another way

Name the constrained types once and reuse them in several endpoints:

```python
ShopId = Annotated[int, Path(ge=1)]
PageSize = Annotated[int, Query(ge=1, le=50)]

def list_products(shop_id: ShopId, size: PageSize = 10, ...): ...
```

The rules then live in one place. (Section 9 goes one step further and puts paging into a dependency.)
