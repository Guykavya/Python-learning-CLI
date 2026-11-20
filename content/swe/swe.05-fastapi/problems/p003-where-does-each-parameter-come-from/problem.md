# Where does each parameter come from?

Chapter section 3.1 (the table "The parameter... is read from") and the beginning of section 6.2 (`loc`). Here is the chapter's `user_posts` endpoint and eight requests. For each request write the **status code**, and then:

- for a **200**: a space and the returned dict, printed as Python prints it (`{'user_id': 7, 'limit': 10, 'draft': False, 'tag': None}`);
- for a **422**: a space and the `loc` of every error, each written as its parts joined with dots (`path.user_id`), separated by single spaces, in the order FastAPI lists them;
- for any other status: nothing more.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/users/{user_id}/posts")
def user_posts(user_id: int, limit: int = 10, draft: bool = False, tag: str | None = None):
    return {"user_id": user_id, "limit": limit, "draft": draft, "tag": tag}


urls = [
    "/users/-3/posts",
    "/users/7/posts?limit=3&draft=yes",
    "/users/7/posts?draft=0&tag=py",
    "/users/7/posts?limit=abc",
    "/users/abc/posts?draft=maybe",
    "/users//posts",
    "/users/7/posts?tag=py&tag=go",
    "/users/7/posts?limit=2.5",
]

client = TestClient(app)
for number, url in enumerate(urls, 1):
    r = client.get(url)
    if r.status_code == 200:
        detail = str(r.json())
    elif r.status_code == 422:
        detail = " ".join(".".join(str(part) for part in e["loc"]) for e in r.json()["detail"])
    else:
        detail = ""
    print(f"{number}: {r.status_code} {detail}".rstrip())
```

Write your answer in `answer.txt`: eight lines, `1: ...` to `8: ...`, in the format of the `print` above. For example a line could be `9: 422 query.size` or `9: 200 {'user_id': 1, 'limit': 5, 'draft': True, 'tag': 'x'}`. Do not run it.

## After you answer

1. `user_id: int` accepted `-3`. What would you add to the signature so that only ids of 1 or more are accepted (section 3.3)?
2. Request 7 sends `tag` twice but the function sees only one value. How would you change the parameter to receive both (section 3.3)?
3. Why is request 6 not a 422 with `loc` `path.user_id`?
