## Hint 1

What does the lock key contain? If each holder puts its **own** random token there, how can `release` tell "my lock" from "somebody else's lock that happens to have the same name"?

## Hint 2

The check must happen inside the same command as the delete. You have such a command:

```text
new_token(): return secrets.token_hex(16)
acquire(r, name, token, ttl): return bool(r.set("lock:"+name, token, ex=ttl, nx=True))
release(r, name, token):      return r.delete_if_equals("lock:"+name, token) == 1
```
