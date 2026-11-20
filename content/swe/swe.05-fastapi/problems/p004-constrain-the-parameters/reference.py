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
