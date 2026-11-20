# Count the calls

Chapter section 9.3 (sub-dependencies, the per-request cache, `use_cache=False`) and "Try it: count the calls" at the end of section 9.

Every dependency below adds 1 to its own counter in `counts` each time it **runs**. Before each request the counters are cleared, and after the request the program prints them. Trace each request through the dependency tree and write what is printed.

Rules from the chapter you need:

- FastAPI resolves an endpoint's parameters **in the order they are written**, and for each one it first resolves that dependency's own sub-dependencies (leaves first).
- Within **one request**, a dependency that was already computed is **not run again**: its cached result is reused.
- `Depends(f, use_cache=False)` always runs `f` again for that one place, even if it already ran in this request.
- A dict keeps its keys in the order they were **first added**, so the names are printed in the order of their **first** run.

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
counts = {}


def note(name):
    counts[name] = counts.get(name, 0) + 1


def get_db():
    note("get_db")
    return "db"


def get_user(db: Annotated[str, Depends(get_db)]):
    note("get_user")
    return "asha"


def get_repo(db: Annotated[str, Depends(get_db)]):
    note("get_repo")
    return "repo"


def get_fresh_repo(db: Annotated[str, Depends(get_db, use_cache=False)]):
    note("get_fresh_repo")
    return "repo"


@app.get("/a")
def a(user: Annotated[str, Depends(get_user)],
      repo: Annotated[str, Depends(get_repo)],
      db: Annotated[str, Depends(get_db)]):
    note("endpoint")
    return "a"


@app.get("/b")
def b(user: Annotated[str, Depends(get_user)],
      repo: Annotated[str, Depends(get_fresh_repo)],
      db: Annotated[str, Depends(get_db)]):
    note("endpoint")
    return "b"


@app.get("/c")
def c(db: Annotated[str, Depends(get_db)],
      db2: Annotated[str, Depends(get_db, use_cache=False)],
      db3: Annotated[str, Depends(get_db, use_cache=False)],
      user: Annotated[str, Depends(get_user)]):
    note("endpoint")
    return "c"


@app.get("/d")
def d(user: Annotated[str, Depends(get_user)],
      again: Annotated[str, Depends(get_user, use_cache=False)]):
    note("endpoint")
    return "d"


client = TestClient(app)
for path in ["/a", "/a", "/b", "/c", "/d"]:
    counts.clear()
    client.get(path)
    line = " ".join(f"{name}={n}" for name, n in counts.items())
    print(f"{path} {line}")
```

Write your answer in `answer.txt`: five lines, one per request, exactly in the format of the `print`: the path, a space, then `name=count` pairs separated by single spaces, in first-run order (for example `/x get_db=1 endpoint=1`). Do not run it.

## After you answer

1. In `/b`, `get_fresh_repo` asks for `get_db` with `use_cache=False`. Why does that make `get_db` run twice, but the endpoint's own `db` parameter does not make it run a third time?
2. In `/d`, `get_user` runs twice. Why does `get_db` still run only once?
3. If `get_db` opened a real database session, what would `use_cache=False` cost you, and when could a second session be what you want?
