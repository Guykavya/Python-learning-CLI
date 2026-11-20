## Approach

The real output (run once to check the hand trace, Python 3.14; the program uses only the standard library):

```text
1. client -> browser: 302 redirect to /authorize [client_id, redirect_uri, response_type, scope, state, code_challenge, code_challenge_method]
2. browser -> auth_server: GET /authorize [client_id, redirect_uri, response_type, scope, state, code_challenge, code_challenge_method]
3. auth_server -> browser: 302 redirect to redirect_uri [code, state]
4. browser -> client: GET /callback [code, state]
5. client -> auth_server: POST /token [grant_type, code, redirect_uri, client_id, code_verifier]
6. auth_server -> client: 200 token response [access_token, token_type, expires_in]
7. client -> resource_server: GET /photos [Authorization]
8. resource_server -> client: 200 photos [owner, photos]
```

How to read it:

1. `connect()` builds `query` and sends it to the browser as a redirect to `/authorize`. The challenge is `s256(verifier)`; the verifier itself is not in the query.
2. The browser follows the redirect: the same seven fields go on to the authorization server. `authorize` prints this line first, **before** it creates the code.
3. The server replies with a redirect to `redirect_uri`. Only `code` and `state` are in it. `authorize` returns exactly those two.
4. The browser hands them to the client (`GET /callback`). Messages 1 to 4 all pass through the browser; anyone who can read the browser's history or URL can see `code`, `state` and `code_challenge`.
5. The client checks `state` (the `assert` prints nothing), then sends the code **and** `code_verifier` straight to the authorization server. This message does not go through the browser.
6. The server pops the code (a code works once), compares `s256(code_verifier)` with the stored challenge, and returns the token fields.
7. The client calls the resource server with the access token in the `Authorization` header.
8. The resource server answers with the data.

Output obtained by running the program with the course virtual environment (Python 3.14). The list is the same on any Python 3 version.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Draw the five lanes of the chapter's diagram (user, browser, client, authorization server, resource server) and put a number on each arrow while you read the code. Then print `step` and compare.
