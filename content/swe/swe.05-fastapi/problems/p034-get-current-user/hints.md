## Hint 1

Draw the dependency tree of `GET /me` (section 9.3): `me` needs `get_current_user`; `get_current_user` needs `oauth2_scheme` (the token) and `get_clock` (the time). Which of these already answers a 401 by itself, and for which case? Which case is left for you?

## Hint 2

`OAuth2PasswordBearer(tokenUrl="token")` is an object you put in `Depends(...)`; it handles "no header". In `get_current_user`, `try: user_id = read_token(token, now) except InvalidToken: raise ...`; then look the user up by id (`next((u for u in USERS.values() if u["id"] == user_id), None)`). For the login, `form: Annotated[OAuth2PasswordRequestForm, Depends()]` gives `form.username` and `form.password`.

## Hint 3

```text
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

POST /token (form = Depends OAuth2PasswordRequestForm, now = Depends get_clock):
    user = USERS.get(form.username)
    if user is None or not verify_password(form.password, user["hash"]): 401 "Incorrect username or password" + Bearer
    return {"access_token": make_token(user["id"], now), "token_type": "bearer"}

get_current_user(token = Depends(oauth2_scheme), now = Depends(get_clock)):
    read_token -> InvalidToken? 401 "Invalid or expired token" + Bearer
    find the user by id; none? same 401
    return user

GET /me (user = Depends(get_current_user)): return {"id", "username"}
```
