## Model answer

**1. Who reads the hints.** The teammate is half right: the Python interpreter ignores type hints at runtime (`double("ab")` returns `"abab"`). But FastAPI reads the endpoint's **signature** when the route is registered and builds **Pydantic** validators from it: `project_id: int` becomes "an int from the path", `task: TaskIn` becomes "a JSON body with these fields and rules". The hints *describe*; Pydantic *enforces*, at the edge of the app, for every request.

**2. Where it happens.** The lifecycle is: (1) routing (404/405), (2) reading the raw pieces and parsing the JSON body (`json_invalid`), (3) Pydantic validation of every parameter and the body, collecting **all** errors, (4) the endpoint, (5) the `response_model` filter. Steps 2 and 3 run **before the endpoint runs**. So inside `create`, `project_id` is a real `int` and `task.priority` is an int from 1 to 5. Repeating those checks in the function is dead code.

**3. What a 422 means.** "Your HTTP request was understood, but the data does not satisfy the declared types and constraints." It is a **client error**: the client must fix its request; the server code did not even run. The body lists every problem; each has `loc` (where: `["body", "priority"]`), `type` (a stable code like `less_than_equal`) and `msg` (a human sentence that may change between versions). Clients should switch on `type` and `loc`.

**4. What it is not.** "Username taken" depends on the **database**, not on the shape of the data: `"asha"` is a perfectly valid username. It is a **business rule**, checked inside the endpoint, and answered with `HTTPException(409)` (Conflict), or 403 for "not allowed". A 422 is not a server bug either: it should be counted in metrics (a spike means a client shipped a broken release) but it does not page anyone, unlike a 500.

**Checklist: your answer should mention**
- [ ] Python ignores hints, but FastAPI reads the signature and Pydantic enforces it at runtime
- [ ] the lifecycle order: routing, reading/parsing, validation, endpoint, response filter
- [ ] validation happens before the endpoint runs, so the function receives clean, typed values
- [ ] a 422 is a client error: well-formed request, data breaks the declared rules; all errors in one response
- [ ] clients use `type` and `loc`, not `msg`
- [ ] business rules that need the database (username taken) are checked in the endpoint and answered with 409 (or 403 / another 4xx), not 422
- [ ] a 422 is not a server bug: count it, do not alert like a 500
