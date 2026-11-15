- Sending `params={"cursor": None, ...}` on the first call. httpx sends that as `cursor=`, an
  empty cursor, which many servers reject or treat as "invalid".
- Writing `while cursor:` with `cursor = None` at the start. The loop body never runs, and
  you return `[]` without making a single request.
- Building the URL with an f-string. `+` in a cursor becomes a space, `&` splits the parameter, and the server says "invalid cursor".
- Decoding or "fixing" the cursor (for example base64-decoding it to read the last id). It is opaque; the format can change any day.
- Using `body["next_cursor"]` when the API leaves the key out on the last answer: `KeyError`.
- Stopping on an empty `items` list. A cursor answer can be empty and still have more after it.
- Forgetting `limit` on the follow-up requests. The server falls back to its default page size, which may be different.
