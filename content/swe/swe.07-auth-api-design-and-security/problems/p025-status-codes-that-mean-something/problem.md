# Status codes that mean something

Chapter section 9.3 and "Try it: status codes". Here is a small FastAPI app and ten requests made with the test client (`raise_server_exceptions=False` makes an unhandled bug come back as a normal 500 response, as a real server would answer). For each request write the **status code**. If the response has a `Location` header or a `Retry-After` header, add its value after a space (the program prints the first one it finds; most responses have neither).

```python
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()
items = {}
calls = {"login": 0}


class ItemIn(BaseModel):
    name: str
    price_cents: int


@app.post("/items", status_code=201)
def create_item(item: ItemIn, response: Response):
    if item.name in items:
        raise HTTPException(409, "name already taken")
    items[item.name] = item.price_cents
    response.headers["Location"] = f"/items/{item.name}"
    return {"name": item.name}


@app.post("/reports", status_code=202)
def start_report():
    return {"status": "queued"}


@app.get("/offers/summer-2019")
def old_offer():
    raise HTTPException(410, "this offer has ended")


@app.put("/items/{name}")
def replace_item(name: str, item: ItemIn, if_match: str = Header(default="")):
    if if_match != "v2":
        raise HTTPException(412, "the item changed, fetch it again")
    return {"name": name}


@app.post("/login")
def login():
    calls["login"] += 1
    if calls["login"] > 2:
        raise HTTPException(429, "too many attempts", headers={"Retry-After": "30"})
    return {"ok": True}


@app.get("/boom")
def boom():
    return {"value": 1 / 0}


client = TestClient(app, raise_server_exceptions=False)
requests = [
    ("POST", "/items", {"json": {"name": "pen", "price_cents": 150}}),
    ("POST", "/reports", {}),
    ("POST", "/items", {"json": {"name": "ink", "price_cents": "cheap"}}),
    ("POST", "/items", {"json": {"name": "pen", "price_cents": 99}}),
    ("GET", "/offers/summer-2019", {}),
    ("PUT", "/items/pen", {"json": {"name": "pen", "price_cents": 99}, "headers": {"If-Match": "v1"}}),
    ("POST", "/login", {}),
    ("POST", "/login", {}),
    ("POST", "/login", {}),
    ("GET", "/boom", {}),
]
for number, (method, path, kwargs) in enumerate(requests, 1):
    r = client.request(method, path, **kwargs)
    extra = r.headers.get("location") or r.headers.get("retry-after") or ""
    print(f"{number}: {r.status_code} {extra}".rstrip())
```

Write your answer in `answer.txt`: ten lines, `1: ...` to `10: ...`, in the format of the `print` at the end. Do not run it.

Things to keep in mind: FastAPI checks the request body against `ItemIn` **before** your function runs. State (`items`, `calls`) is changed by earlier requests and seen by later ones.

## After you answer

1. Requests 3 and 4 are both "your data is wrong". Why is one `422` and the other `409`? Who detects each one?
2. What is the difference between `201` and `202`? When would you choose `202` for a real endpoint?
3. Request 10 is a bug in the server. Why must the client see `500` and never `200` with an error text?
