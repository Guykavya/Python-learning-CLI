# Field constraints and aliases

Chapter sections 5.3 (`Field`) and 5.10 (aliases, `populate_by_name`). The mobile team sends JSON in camelCase (`"userName"`), the web team in snake_case (`"user_name"`). Accept both.

In `solution.py` define `app = FastAPI()` and a model `SignupIn`:

| Python name | JSON name(s) | Type and rules | Default |
|---|---|---|---|
| `user_name` | `"userName"` **and** `"user_name"` | str, 3 to 20 characters | required |
| `age` | `"age"` | int, from 13 to 120 | required |
| `bio` | `"bio"` | str, at most 50 characters | `""` |

Use `Field(...)` for the rules and `alias="userName"`, plus `model_config = ConfigDict(populate_by_name=True)` so that the Python name is accepted too.

`POST /signups` takes a `SignupIn` body and returns `data.model_dump()` (Python names) with status **201**.

The tests check each rule's 422 (`loc` and `type` only). Notice: the error `loc` uses the **alias**, `["body", "userName"]`, because that is the name the API documents.

## Example

```text
POST /signups {"userName": "asha_k", "age": 21}
-> 201 {"user_name": "asha_k", "age": 21, "bio": ""}

POST /signups {"user_name": "ravi", "age": 30, "bio": "hi"}
-> 201 {"user_name": "ravi", "age": 30, "bio": "hi"}

POST /signups {"userName": "ab", "age": 12}
-> 422  ["body", "userName"] string_too_short
        ["body", "age"]      greater_than_equal
```
