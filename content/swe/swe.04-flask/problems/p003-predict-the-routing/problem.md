# Predict the routing

Chapter sections 3.4 to 3.8. Here is a Flask app and eight requests made with the test client. For each request write the **status code**, and then:

- for a **redirect** (301, 302, 308): a space and the value of the `Location` header, exactly as the test client shows it (chapter section 3.5 shows what a 308 looks like);
- for a **200**: a space and the response body;
- for any other status (404, 405): nothing more.

```python
from flask import Flask, redirect, url_for

app = Flask(__name__)


@app.route("/about/")
def about():
    return "about"


@app.route("/contact")
def contact():
    return "contact"


@app.route("/old")
def old():
    return redirect(url_for("new"))


@app.route("/new")
def new():
    return "new page"


@app.route("/moved")
def moved():
    return redirect(url_for("new"), code=301)


@app.route("/item/<int:n>")
def item(n):
    return f"item {n}"


@app.route("/submit", methods=["POST"])
def submit():
    return "saved"


client = app.test_client()
requests = [
    ("GET", "/about"),
    ("GET", "/about/"),
    ("GET", "/contact/"),
    ("GET", "/old"),
    ("GET", "/moved"),
    ("GET", "/item/x"),
    ("GET", "/submit"),
    ("POST", "/submit"),
]
for number, (method, path) in enumerate(requests, 1):
    r = client.open(path, method=method)
    if r.status_code in (301, 302, 308):
        detail = r.headers["Location"]
    elif r.status_code == 200:
        detail = r.get_data(as_text=True)
    else:
        detail = ""
    print(f"{number}: {r.status_code} {detail}".rstrip())
```

Write your answer in `answer.txt`: eight lines, `1: ...` to `8: ...`, in the format of the `print` above. Do not run it.

## After you answer

1. Why does `/about` redirect while `/contact/` is a 404? Which rule has the trailing slash?
2. What is the difference between the 302 and the 301 here, for a browser or a search engine?
3. A 404 and a 405 both mean "no": what does each tell the client?
