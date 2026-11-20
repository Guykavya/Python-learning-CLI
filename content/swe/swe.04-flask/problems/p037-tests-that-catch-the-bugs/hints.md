## Hint 1

Which sentence of the problem describes each broken app? For each bug, which single request would behave differently on the broken app than on the correct one? That request is the heart of the check.

## Hint 2

Helpers keep the checks short: `token(client)` (GET `/csrf`), `log_in(client, user, password)`. Remember: **login clears the session**, so ask for a new token after logging in. For the CSRF bug that ignores the value, a "missing token" test is not enough: send `"wrong-token"` as well.

## Hint 3

```text
check_login:   login ok -> 200; create post -> 201;  wrong password on another client -> 401 and create post -> 401
check_csrf:    login; POST /posts without token -> 400; with "wrong-token" -> 400; with the real token -> 201
check_owner_only: asha and ravi log in; asha creates (id); ravi deletes -> 403; asha deletes -> 204
```
