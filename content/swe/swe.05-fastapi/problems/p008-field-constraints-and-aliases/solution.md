## Approach

Put every rule on its field with `Field`, and give `user_name` an alias plus `populate_by_name`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class SignupIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_name: str = Field(min_length=3, max_length=20, alias="userName")
    age: int = Field(ge=13, le=120)
    bio: str = Field(default="", max_length=50)


@app.post("/signups", status_code=201)
def signup(data: SignupIn):
    return data.model_dump()
```

Example: `{"userName": "ab", "age": 12}` breaks two rules; both are reported, the first at `["body", "userName"]` (the alias is the public name) with type `string_too_short`, the second at `["body", "age"]` with `greater_than_equal`.

`model_dump()` uses the Python names; `model_dump(by_alias=True)` would give `userName` back.

## Complexity

O(size of the body).

## Another way

Instead of one alias per field, set `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` (section 5.10). Every snake_case field then gets its camelCase alias automatically, which is what you want when a whole API speaks camelCase.
