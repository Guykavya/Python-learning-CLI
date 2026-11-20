## Hint 1

The pattern of section 3.3 is `name: Annotated[<type>, <Query or Path>(<rules>)] = <default>`. Which rule names are for numbers (`ge`, `le`, `gt`, `lt`) and which are for strings (`min_length`, `max_length`, `pattern`)?

## Hint 2

The list needs two things: the type `list[str] | None` **and** `Query()`. Without `Query()`, FastAPI thinks a `list[str]` parameter is a JSON body. Return `tag or []` so that "no tag" becomes an empty list.

## Hint 3

```text
shop_id: Annotated[int, Path(ge=1)]
q:       Annotated[str | None, Query(min_length=2, max_length=30, pattern="^[a-z0-9 ]+$")] = None
page:    Annotated[int, Query(ge=1)] = 1
size:    Annotated[int, Query(ge=1, le=50)] = 10
tag:     Annotated[list[str] | None, Query()] = None
return {..., "tags": tag or []}
```
