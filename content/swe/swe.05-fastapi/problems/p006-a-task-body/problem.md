# A task body

Chapter sections 4.1 and 4.3, 5.2 (defaults) and 7.6 (status codes). In `solution.py` define:

```python
class TaskIn(BaseModel):
    title: str
    priority: int = 3
    tags: list[str] = []

TASKS: dict[int, dict] = {}     # the "database": id -> stored task
app = FastAPI()
```

and two endpoints:

- `POST /tasks` takes a `TaskIn` body. It gives the task the next id (`len(TASKS) + 1`), stores `{"id": ..., "title": ..., "priority": ..., "tags": [...]}` in `TASKS`, and returns that dict with status **201 Created** (`status_code=201` on the decorator).
- `GET /tasks` returns the list of stored tasks, in id order.

You write **no checking code**: FastAPI and Pydantic refuse bad bodies with a 422 before your function runs, so nothing is stored. The tests check these cases (`loc` and `type` only):

| Body sent | `loc` | `type` |
|---|---|---|
| no `title` | `["body", "title"]` | `missing` |
| `"tags": "home"` (not a list) | `["body", "tags"]` | `list_type` |
| form data `title=x` instead of JSON | `["body"]` | `model_attributes_type` |
| a JSON **list** `[{"title": "x"}]` | `["body"]` | `model_attributes_type` |

The last two say "the body as a whole is not an object with fields".

The tests empty `TASKS` before each test, so ids start at 1.

## Example

```text
POST /tasks {"title": "buy milk"}
-> 201 {"id": 1, "title": "buy milk", "priority": 3, "tags": []}

POST /tasks {"title": "pay rent", "priority": "1", "tags": ["home", "money"]}
-> 201 {"id": 2, "title": "pay rent", "priority": 1, "tags": ["home", "money"]}
   ("1" became 1: lax mode, section 4.1)

GET /tasks -> 200 [ ...both tasks... ]
```
