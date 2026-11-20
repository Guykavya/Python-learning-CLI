## Hint 1

Start at the last line, `Client(AuthServer()).connect()`. Which method runs first, and what is the first `send` inside it? Write that line before reading further.

## Hint 2

`self.auth.authorize(query)` is called in the middle of `connect`. Everything it prints comes **before** the next `send` of `connect`. Do the same for `self.auth.token(form)`. Note where the `send` calls are inside `authorize` and `token`: some are at the top of the function, some at the end.

## Hint 3

```text
connect:  send 1 (client -> browser)
  authorize: send 2 (browser -> auth_server), then send 3 (auth_server -> browser)
connect:  send 4 (browser -> client)
  token:     send 5 (client -> auth_server), then send 6 (auth_server -> client)
connect:  send 7, send 8 (client <-> resource_server)
Field lists: copy the keys of the dicts in the order they are written.
```
