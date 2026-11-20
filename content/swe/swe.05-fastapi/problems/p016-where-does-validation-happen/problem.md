# Where does validation happen?

Chapter sections 5.1 (hints describe; Pydantic enforces), 6.1 (the request lifecycle) and 6.3 (what a 422 is NOT). A teammate looks at this code and says: "Python ignores type hints, so `priority: int` does nothing. We must check every field inside the function. And when someone registers a username that is already taken we should also answer 422, because it is a validation error."

```python
class TaskIn(BaseModel):
    title: str = Field(min_length=3)
    priority: int = Field(ge=1, le=5)


@app.post("/projects/{project_id}/tasks", status_code=201)
def create(project_id: int, task: TaskIn):
    ...
```

In `answer.md` write a clear explanation (about 150 to 300 words) that answers:

1. **Who reads the type hints**, and when? Is the teammate right that Python ignores them? Why does `priority: int` still matter here?
2. **Where in the request lifecycle** does validation happen, and what does that guarantee about the code inside `create`? Name the steps of section 6.1 in order.
3. **What does a 422 mean**, and who has to fix it, the client or the server? What does it say about `msg`, `loc` and `type`?
4. **What a 422 is not:** why is "username taken" (or "project is archived") **not** a 422, and which status should it get? Why is a 422 not something to page an engineer about, like a 500?

A good answer uses the words *type hint*, *Pydantic*, *before the endpoint runs*, *client error*, *business rule*, *409*.

## Example

A sentence in the expected style: "Python itself ignores the hint, but FastAPI reads the signature when the route is registered and builds a Pydantic validator from it, so ..."
