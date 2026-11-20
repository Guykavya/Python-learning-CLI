from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


# TODO: add the rules with Annotated[..., Path(...)] and Annotated[..., Query(...)],
# and make `tag` a list read from the query string.
@app.get("/shops/{shop_id}/products")
def list_products(shop_id: int, q: str | None = None, page: int = 1, size: int = 10, tag: str | None = None):
    return {"shop_id": shop_id, "q": q, "page": page, "size": size, "tags": [tag] if tag else []}
