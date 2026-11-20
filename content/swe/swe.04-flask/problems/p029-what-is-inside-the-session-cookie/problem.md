# What is inside the session cookie?

Chapter sections 16.2 and 16.6. A Flask app (`SECRET_KEY = "course-demo-key"`) sent this cookie after a login:

```text
session=eyJyb2xlIjoibWVtYmVyIiwidXNlcl9pZCI6N30.av7iBw.SMsPfJaVXGTtV7dWKc8Z7sRIn2Y
```

It has three parts separated by dots. You may use a few lines of Python to look inside (`base64`, `itsdangerous.base64_decode`, `json`), but the task is to **explain**, in `answer.md` (about 200 to 300 words):

1. What does each of the three parts contain? Decode the first one and write what you find (the first and third are Base64-URL; the second is a small number).
2. The cookie is **signed, not encrypted**. What does that allow the user (or anyone who sees the cookie) to do, and what does it forbid?
3. What changes if your `SECRET_KEY` is leaked, or is a weak value such as `"dev"`?
4. Why should the session hold only a **user id** and not the role, the price of the cart, or the password? (Hint: what is checked on every request, and who can read the cookie?)
5. Why does the login view call `session.clear()` before it sets `session["user_id"]`? Name the attack (**session fixation**) and what it needs.

A good answer shows the decoded payload and uses the words *signature*, *secret key*, *forge*, *tamper*, *fixation*.
