## Hint 1

Go endpoint by endpoint and list its function parameters. For each one ask the section 3.1 question: is it in the path template? Is it a Pydantic model (then it is the body)? Is it marked `Header()`? Otherwise it is a query parameter. Then: does it have a default (optional) or not (required)? A path parameter is always required.

## Hint 2

- `Header()` turns underscores into hyphens: the spec names the header the way clients send it.
- The success code is `status_code=` of the decorator (200 when not given). `responses={...}` adds documented codes.
- FastAPI adds `422` ("Validation Error") to an operation only when there is **something to validate**: at least one parameter or a body. It also adds the two schemas that describe a 422 body.
- The loop sorts paths, then methods (alphabetically, in lower case), so the order is not the order in the source.

## Hint 3

```text
paths sorted: /tasks, /tasks/{task_id};  methods sorted: get < post;  delete
GET    /tasks            no inputs            -> 200 only
POST   /tasks            header x-user + body -> 201 and 422
DELETE /tasks/{task_id}  task_id path; force query optional -> 204, the documented 404, 422
schemas: your two models + the two that describe a 422
```
