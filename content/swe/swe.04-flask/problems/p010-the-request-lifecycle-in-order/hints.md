## Hint 1

Draw the lifecycle of section 5.6 and walk each request down it. At which box does each hook sit? At which box does an error handler sit?

## Hint 2

An error handler produces the **response**; after that the request continues normally: `after_request` sees that response. `teardown_request` runs last and receives an exception **only when it escaped** (was not handled). Routing errors (`404`) are raised when Flask tries to *dispatch*, after `before_request`.

## Hint 3

```text
/ok       before, view, after, teardown
/missing  before, (no view: the 404 is raised) handler 404, after, teardown
/value    before, view, handler ValueError, after, teardown (handled: no exception)
/crash    before, view, (no handler: 500 page) after, teardown with the RuntimeError
```
