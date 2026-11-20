# 401, 403 or 404?

Chapter section 7.5 and "Try it: the 403 that leaks". Here is a small FastAPI app and six requests made with the test client. For each request, write the status code and the message the program prints. The message is the `detail` of an error, or, for the one success, the `owner` of the order.

```python
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

TOKENS = {"t-ada": ("ada", "customer"), "t-bo": ("bo", "customer")}
ORDERS = {1: {"owner": "ada", "total": 2500}, 2: {"owner": "bo", "total": 990}}
app = FastAPI()


def current_user(authorization: str = Header(default="")):
    user = TOKENS.get(authorization.removeprefix("Bearer "))
    if user is None:
        raise HTTPException(401, "login required")
    return user


@app.get("/orders/{order_id}")
def get_order(order_id: int, user=Depends(current_user)):
    order = ORDERS.get(order_id)
    if order is None or order["owner"] != user[0]:
        raise HTTPException(404, "order not found")
    return order


@app.get("/admin/users")
def admin_users(user=Depends(current_user)):
    if user[1] != "admin":
        raise HTTPException(403, "admins only")
    return ["ada", "bo"]


client = TestClient(app)
requests = [
    ("GET", "/orders/1", {}),
    ("GET", "/orders/1", {"Authorization": "Bearer t-nobody"}),
    ("GET", "/orders/1", {"Authorization": "Bearer t-bo"}),
    ("GET", "/admin/users", {"Authorization": "Bearer t-ada"}),
    ("GET", "/orders/99", {"Authorization": "Bearer t-ada"}),
    ("GET", "/orders/1", {"Authorization": "Bearer t-ada"}),
]
for number, (method, path, headers) in enumerate(requests, 1):
    r = client.request(method, path, headers=headers)
    body = r.json()
    detail = body["detail"] if "detail" in body else body["owner"]
    print(f"{number}: {r.status_code} {detail}")
```

Write your answer in `answer.txt`: six lines in the format of the `print` at the end (`1: <status> <text>`). Do not run it.

Notes for the trace: `TOKENS` maps a token to `(name, role)`. A dependency (`current_user`) runs before the function body. `Header(default="")` means a missing header is an empty string.

## After you answer

1. Requests 3 and 5 give the same answer. Why is that on purpose? What would an attacker learn if request 3 answered `403`?
2. Requests 1 and 2 fail in different ways (no token, an unknown token). Why are both `401` and not `403`?
3. Request 4 is a `403`, and not a `404`. What is different about `/admin/users` compared with somebody else's order?
