# What will CORS allow?

Chapter section 13.2. Here is an API protected by `CORSMiddleware` and five requests made with the test client, as a browser would send them. Requests 1 and 2 are **simple requests** (a plain GET with an `Origin` header). Requests 3 to 5 are **preflights**: an `OPTIONS` request with an `Access-Control-Request-Method` header, which a browser sends to ask "may I send this method from this origin?" before the real request.

For each request write the **status code** and the value of the **`Access-Control-Allow-Origin`** response header, or `none` if the response has no such header.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
)


@app.get("/data")
def data():
    return {"ok": True}


@app.post("/data")
def save():
    return {"saved": True}


APP = "https://app.example.com"
EVIL = "https://evil.example"

client = TestClient(app)
requests = [
    ("GET", APP, None),
    ("GET", EVIL, None),
    ("OPTIONS", APP, "POST"),
    ("OPTIONS", APP, "DELETE"),
    ("OPTIONS", EVIL, "GET"),
]
for number, (method, origin, wanted) in enumerate(requests, 1):
    headers = {"Origin": origin}
    if wanted is not None:
        headers["Access-Control-Request-Method"] = wanted      # this makes it a preflight
    r = client.request(method, "/data", headers=headers)
    allow = r.headers.get("access-control-allow-origin", "none")
    print(f"{number}: {r.status_code} {allow}")
```

Write your answer in `answer.txt`: five lines, `1: ...` to `5: ...`, in the format of the `print` above (for example `7: 200 none`). Do not run it.

## After you answer

1. Request 2 got a 200, and the endpoint really ran. So what exactly does CORS protect, and who enforces it?
2. In request 4 the origin is allowed but the method is not. Why does the browser still refuse to send the real `DELETE`, even though the response names the origin?
3. What would `client.options("/data", headers={"Origin": APP})` (no `Access-Control-Request-Method`) return, and why is it not treated as a preflight?
