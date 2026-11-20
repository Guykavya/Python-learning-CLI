## Hint 1

Section 5.3: `Field(...)` takes the same rule names as `Query` (`ge`, `le`, `min_length`, `max_length`). Where does the default go when you use `Field` as the value: `bio: str = Field(default="", max_length=50)`?

## Hint 2

`alias="userName"` makes Pydantic read the JSON key `userName`, and **only** that key. Which `ConfigDict` option (section 5.10) also allows the Python name?

## Hint 3

```text
class SignupIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_name: str = Field(min_length=3, max_length=20, alias="userName")
    age: int = Field(ge=13, le=120)
    bio: str = Field(default="", max_length=50)
```
