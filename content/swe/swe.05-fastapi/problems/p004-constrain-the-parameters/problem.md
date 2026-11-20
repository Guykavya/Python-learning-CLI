# Constrain the parameters

Chapter section 3.3 (`Query`, `Path` and `Annotated`) and section 6.2 (`loc` and `type`). In `solution.py` define `app = FastAPI()` with one endpoint:

`GET /shops/{shop_id}/products`

| Parameter | From | Type and rules | Default |
|---|---|---|---|
| `shop_id` | path | int, at least 1 | required |
| `q` | query | str or None, 2 to 30 characters, only `a-z`, `0-9` and spaces (`pattern="^[a-z0-9 ]+$"`) | `None` |
| `page` | query | int, at least 1 | `1` |
| `size` | query | int, from 1 to 50 | `10` |
| `tag` | query | a **list** of str, sent as `?tag=a&tag=b` | `None` |

Use `Annotated[..., Path(...)]` and `Annotated[..., Query(...)]` for every rule. The endpoint returns

```python
{"shop_id": shop_id, "q": q, "page": page, "size": size, "tags": tag or []}
```

Every bad value must be refused by FastAPI with a **422** before your function runs. The tests check the `loc` and the `type` of each error (not the human `msg`):

| Bad value | `loc` | `type` |
|---|---|---|
| `shop_id` 0 | `["path", "shop_id"]` | `greater_than_equal` |
| `size` 51 | `["query", "size"]` | `less_than_equal` |
| `q` too short / too long | `["query", "q"]` | `string_too_short` / `string_too_long` |
| `q` with a capital letter | `["query", "q"]` | `string_pattern_mismatch` |

## Example

```text
GET /shops/3/products?q=red shoe&tag=sale&tag=new
-> 200 {"shop_id": 3, "q": "red shoe", "page": 1, "size": 10, "tags": ["sale", "new"]}

GET /shops/0/products?size=51
-> 422 with two errors: ["path", "shop_id"] greater_than_equal, ["query", "size"] less_than_equal
```
