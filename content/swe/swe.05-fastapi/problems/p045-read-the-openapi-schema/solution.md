## Approach

Classify every parameter, then add what FastAPI adds on its own.

```text
GET /tasks | required: - | optional: - | responses: 200
POST /tasks | required: x-user(header), body | optional: - | responses: 201,422
DELETE /tasks/{task_id} | required: task_id(path) | optional: force(query) | responses: 204,404,422
schemas: HTTPValidationError, TaskIn, TaskOut, ValidationError
```

- **Order.** `sorted` on the paths gives `/tasks` before `/tasks/{task_id}`; on the methods `get` before `post`. So GET comes first although POST could be written first in the source.
- **GET /tasks.** No parameters, no body. Nothing can be invalid, so FastAPI documents only the success code **200**: no 422.
- **POST /tasks.** `task: TaskIn` is a Pydantic model, so it is the **request body** (required, because it has no default). `x_user: Annotated[str, Header()]` is a required header; FastAPI converts the underscore to a hyphen, so the spec (and the client) uses **`x-user`**. Success is **201** (`status_code=201`), and a **422** is added because there are inputs to validate.
- **DELETE /tasks/{task_id}.** `task_id` appears in the path template: a **path** parameter, always required. `force` has a default: an optional **query** parameter. Codes: **204** (the decorator), **404** (from `responses=`; it only documents, it does not make the endpoint return 404), **422** (added).
- **Schemas.** `TaskIn` (request body) and `TaskOut` (response model), plus `HTTPValidationError` (the `{"detail": [...]}` body of a 422) and `ValidationError` (one item of that list), which FastAPI adds as soon as any operation can answer 422.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise. (`app.openapi()` builds the document once and caches it in `app.openapi_schema`.)

## Another way

Look at the raw JSON instead of a summary: `print(json.dumps(app.openapi()["paths"]["/tasks"]["post"], indent=2))` shows the `parameters` list, the `requestBody` with its `$ref` to `TaskIn`, and every response with its description. Or open `/docs` in a browser (needs the internet for the Swagger files, section 19.2) and read the same facts as a page.
