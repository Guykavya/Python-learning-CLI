## Approach

First write the shape each endpoint expects, then compare every request with it.

| Endpoint | Body parameters | Expected JSON |
|---|---|---|
| `/a` | one model | `{"name": "lamp"}` |
| `/b` | two models | `{"item": {"name": "lamp"}, "user": {"username": "kavya"}}` |
| `/c` | one model, `embed=True` | `{"item": {"name": "lamp"}}` |
| `/d` | a model and a `Body()` int | `{"item": {"name": "lamp"}, "count": 2}` |

```text
1: 200 lamp
2: 422 body.name:missing
3: 200 lamp for kavya
4: 422 body.item:missing body.user:missing
5: 422 body.item:missing
6: 200 lamp
7: 200 2 x lamp
8: 422 body.item:missing
9: 422 body.count:missing
```

- **1, 2.** `/a` reads the whole object as `Item`. Request 2 wraps it under `"item"`, so `Item` finds no `name`: `body.name:missing` (the extra key `item` is ignored).
- **3, 4.** `/b` has two body parts, so each lives under its parameter name. Request 4 is "flat": both parts are missing, and **both** errors are reported.
- **5, 6.** `embed=True` asks for the wrapped shape even with one model. Request 5 is flat, so `item` is missing.
- **7, 8, 9.** `count: Annotated[int, Body()]` is a second body part, so `/d` behaves like `/b`. Request 8 has `count` but not `item`; request 9 has `item` but not `count`. Without `Body()` FastAPI would read `count` from the **query string** (section 3.1), and the body would be the bare `Item`.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Make one model for the whole body: `class Order(BaseModel): item: Item; count: int`, and a single parameter `order: Order`. Then the shape is written down in one place, it shows as one schema in `/docs`, and there is no "one part or several parts" rule to remember. Many teams prefer this.
