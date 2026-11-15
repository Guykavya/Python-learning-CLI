- Parsing before `raise_for_status()`. A 404 HTML page then shows up as "not JSON" and the real
  problem (a wrong path, a missing order) is hidden.
- Returning the JSON of a 500 answer. `{"error": "database down"}` is not data; loading it
  quietly puts an error message into your tables.
- Building the URL by hand (`f"{path}?page={page}"`). `params=` encodes special characters
  correctly and leaves the query string out when there are no parameters.
- Catching `Exception` around the parse. That also hides bugs in your own code; catch the
  parse error (`ValueError`) only.
- Putting the whole body in the error message. One HTML page can be megabytes; `body[:80]` is enough to recognise it.
- Raising a new error without `from error`. The traceback then says "during handling of the
  above exception, another exception occurred", which looks like a second bug.
- Calling `response.json()` on a 204. There is no body, so it raises; 204 means "done, nothing to return".
