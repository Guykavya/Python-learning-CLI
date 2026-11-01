- Forgetting `raise_for_status()`. httpx happily returns a 404 response; your code then returns
  `{"error": "not found"}` as if it were the user.
- Writing `async with httpx.AsyncClient() as client:` inside the function. It ignores the
  client you were given, opens a new connection pool for every call, and goes to the real
  network in the tests.
- Forgetting `await` in front of `client.get(url)`. You get a coroutine object, and
  `.raise_for_status()` fails with `AttributeError: 'coroutine' object has no attribute ...`.
- Returning `response.text` or `response`. The caller asked for decoded JSON.
- Writing `await response.json()`. `.json()` is a plain method on an already-read response;
  only the request itself is awaited.
