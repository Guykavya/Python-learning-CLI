# The authorisation code flow, in order

Chapter sections 5.2 and 5.3. Below is a small in-process model of the OAuth2 authorization code flow with PKCE. Every message between two parties goes through `send(...)`, which prints one line: a running number, `sender -> receiver`, a short message text, and in square brackets the **names of the fields** the message carries, in the order the code lists them. (The user is already logged in and has pressed "Allow".)

```python
import base64
import hashlib

step = 0


def send(sender, receiver, message, fields):
    """Print one message of the flow: who sends what to whom, and which fields it carries."""
    global step
    step += 1
    print(f"{step}. {sender} -> {receiver}: {message} [{', '.join(fields)}]")


def s256(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()


class AuthServer:
    def __init__(self):
        self.codes = {}

    def authorize(self, query):
        """The user is already logged in and has pressed 'Allow'."""
        send("browser", "auth_server", "GET /authorize", list(query))
        code = "CODE-1"
        self.codes[code] = {"challenge": query["code_challenge"], "redirect_uri": query["redirect_uri"]}
        send("auth_server", "browser", "302 redirect to redirect_uri", ["code", "state"])
        return {"code": code, "state": query["state"]}

    def token(self, form):
        send("client", "auth_server", "POST /token", list(form))
        entry = self.codes.pop(form["code"])
        assert s256(form["code_verifier"]) == entry["challenge"]
        reply = {"access_token": "AT-1", "token_type": "Bearer", "expires_in": 600}
        send("auth_server", "client", "200 token response", list(reply))
        return reply


class Client:
    def __init__(self, auth):
        self.auth = auth
        self.verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        self.state = "xyz789"

    def connect(self):
        query = {
            "client_id": "printshop",
            "redirect_uri": "https://print.example/callback",
            "response_type": "code",
            "scope": "photos:read",
            "state": self.state,
            "code_challenge": s256(self.verifier),
            "code_challenge_method": "S256",
        }
        send("client", "browser", "302 redirect to /authorize", list(query))
        back = self.auth.authorize(query)
        send("browser", "client", "GET /callback", list(back))
        assert back["state"] == self.state
        form = {
            "grant_type": "authorization_code",
            "code": back["code"],
            "redirect_uri": query["redirect_uri"],
            "client_id": "printshop",
            "code_verifier": self.verifier,
        }
        token = self.auth.token(form)
        send("client", "resource_server", "GET /photos", ["Authorization"])
        send("resource_server", "client", "200 photos", ["owner", "photos"])
        return token


Client(AuthServer()).connect()
```

Write in `answer.txt` exactly what the program prints: **8 lines**, one per message, in the format of `send`. Follow the code with a finger: which `send` runs first? Which call happens **inside** another call? The order of the printed lines is the order the code runs, not the order the functions appear in the file. Do not run it.

## After you answer

1. Which fields travel through the browser (messages 2 to 4), and which two secrets never do? Why is that the point of PKCE?
2. Message 1 carries `state`, and message 4 carries it back. What does the client do with it, and which attack does that stop?
3. Why is `code_verifier` sent in message 5 but only `code_challenge` in message 1?
