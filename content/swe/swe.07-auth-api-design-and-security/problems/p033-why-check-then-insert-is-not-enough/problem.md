# Why "check, then insert" is not enough

Chapter sections 13.1 to 13.4 and "Try it: what is wrong with this design?". A developer protects `POST /payments` against double charges with this code:

```python
def create_payment(db, user_id, key, amount):
    if not db.execute("SELECT 1 FROM idempotency WHERE user_id = ? AND key = ?", (user_id, key)).fetchone():
        charge(user_id, amount)                                    # moves the money
        db.execute("INSERT INTO idempotency (user_id, key) VALUES (?, ?)", (user_id, key))
        db.commit()
        return "charged"
    return "already done"
```

The idea is right, the code is not. In `answer.md` write a clear explanation (about 150 to 300 words) that covers:

1. **Why the client cannot tell** "the payment failed" from "the payment succeeded but the reply was lost", and why simply retrying is dangerous without a key.
2. **What an idempotency key does:** what the client sends, what the server remembers, what a repeat gets back.
3. **The race:** how two requests with the same key can both charge, step by step. Name the gap in the code above.
4. **The crash gap:** what happens if the process dies between `charge(...)` and the `INSERT`.
5. **The fix:** why the key must be claimed with one atomic step (a unique constraint) *before* the work, and why the work and the "completed" mark must belong together (one transaction, or pass the key on to the outside system).

A good answer uses the words *retry*, *race*, *unique constraint*, *atomic*, *transaction*.
