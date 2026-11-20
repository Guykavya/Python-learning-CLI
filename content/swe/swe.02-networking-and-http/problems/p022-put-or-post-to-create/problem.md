# PUT or POST to create?

An API lets clients create books. Two designs are possible (chapter sections 9.4 and 21.5):

```text
Design 1:  POST /books            body {"title": "Dune"}      -> 201, Location: /books/42
Design 2:  PUT  /books/42         body {"title": "Dune"}      -> 201 (or 200 if it already existed)
```

In `answer.md` (8 to 12 sentences), explain:

1. **Who chooses the id** in each design?
2. A client sends the create request, the network drops the **reply**, and the client sends the same request again. What happens in each design?
3. Why is `PUT /books/42` called idempotent and `POST /books` not?
4. How does an **idempotency key** make the `POST` design safe to retry? Describe what the server stores and what it does when the same key arrives a second time.
5. When would you still choose `POST`?
