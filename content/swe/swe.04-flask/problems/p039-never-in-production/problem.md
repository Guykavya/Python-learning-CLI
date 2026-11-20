# Never in production

Chapter sections 22.2 and 22.3. A teammate deploys with this `app.py` and says "it works on the server":

```python
from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"

@app.route("/")
def home():
    return "hello"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
```

In `answer.md` (about 250 words) explain:

1. **What is dangerous about `debug=True`?** Name the interactive debugger and what an attacker who reaches it can do; and what an error page shows to everyone else. (The console PIN is not a defence you can rely on.)
2. **What is wrong with `app.run(...)` and the development server** as a way to serve real users? Name at least two problems (think of how many requests it handles, hardening, TLS, restarts).
3. **What replaces them?** Describe the usual stack: an application server such as **Gunicorn** (workers, timeouts, how it imports your app with `create_app()`), in front of a **reverse proxy** (nginx or a cloud load balancer) that does TLS and slow clients.
4. **How do you keep debug mode off by accident?** Where does the switch come from, and what else is wrong in the snippet (look at the secret key and the host).
