# Several body parts

Chapter section 4.2 (several body parts and `Body`), with 4.1 and the `loc` of section 6.2. The **shape** of the JSON an endpoint expects depends on how many body parameters it has. Here are four endpoints and nine requests. For each request write the **status code** and then a space and:

- for a **200**: the returned value as the program prints it (a plain string, no quotes);
- for a **422**: every error written as `loc` parts joined with dots, a colon, and the error `type` (`body.name:missing`), separated by single spaces, in FastAPI's order.

```python
from typing import Annotated

from fastapi import Body, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str


class User(BaseModel):
    username: str


@app.post("/a")
def one_model(item: Item):
    return item.name


@app.post("/b")
def two_models(item: Item, user: User):
    return f"{item.name} for {user.username}"


@app.post("/c")
def embedded(item: Annotated[Item, Body(embed=True)]):
    return item.name


@app.post("/d")
def model_and_number(item: Item, count: Annotated[int, Body()]):
    return f"{count} x {item.name}"


requests = [
    ("/a", {"name": "lamp"}),
    ("/a", {"item": {"name": "lamp"}}),
    ("/b", {"item": {"name": "lamp"}, "user": {"username": "kavya"}}),
    ("/b", {"name": "lamp", "username": "kavya"}),
    ("/c", {"name": "lamp"}),
    ("/c", {"item": {"name": "lamp"}}),
    ("/d", {"item": {"name": "lamp"}, "count": 2}),
    ("/d", {"name": "lamp", "count": 2}),
    ("/d", {"item": {"name": "lamp"}}),
]

client = TestClient(app)
for number, (path, body) in enumerate(requests, 1):
    r = client.post(path, json=body)
    if r.status_code == 200:
        detail = r.json()
    else:
        detail = " ".join(".".join(map(str, e["loc"])) + ":" + e["type"] for e in r.json()["detail"])
    print(f"{number}: {r.status_code} {detail}")
```

Write your answer in `answer.txt`: nine lines, `1: ...` to `9: ...`, in the format of the `print` above (for example `10: 422 body.size:missing` or `10: 200 cup`). Do not run it.

## After you answer

1. Write the JSON body that `/a`, `/b`, `/c` and `/d` each expect, one line each.
2. Why does `/c` expect `{"item": {...}}` although it has only one model? When would you want that?
3. Request 8 sends `name` at the top level. Why does FastAPI not "find" it?
