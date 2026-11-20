# Validation tests that catch mutants

Chapter sections 20.1 (parametrised validation tests), 5.3 (`Field` constraints) and 6.2 (the 422). How do you know your tests are good? **Mutation testing** answers: make small, plausible bugs in the code ("mutants"), run the tests against each one, and see whether some test fails. A mutant that passes every test **survives**: your tests would not notice that bug either.

This time you write only **test data**. In `solution.py` define

```python
CASES = [(payload, expected_status), ...]
```

Each `payload` is sent as the JSON body of `POST /tasks`; `expected_status` is `201` (accepted) or `422` (refused). The test file holds the **correct** app and **four mutant apps**; you cannot see the mutants in your file, only the rules of the correct app:

| Field | Rule in the correct app |
|---|---|
| `title` | required string, **1 to 100** characters |
| `priority` | integer **1 to 5**, default 3 |
| `tags` | list of strings, default `[]` |
| anything else | **refused**: unknown fields are an error (`extra="forbid"`) |

```python
class TaskIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=100)
    priority: int = Field(default=3, ge=1, le=5)
    tags: list[str] = []
```

The tests check:

1. Every case gives exactly its `expected_status` on the **correct** app (your expectations must be right).
2. There is at least one `201` case and one `422` case (an app that refuses everything must not pass).
3. Each of the four mutants is **caught**: at least one of your cases gets a different status from the mutant than you expected. Each mutant loosens **one** rule of the table; some loosen it by just one step. The failure message names the mutant that survived.
4. At most 25 cases: think, do not spray.

## Example

```python
CASES = [
    ({"title": "Write tests"}, 201),
    ({"priority": 2}, 422),             # title is missing
]
```

These two cases are correct for the correct app, but they catch no mutant. Which values sit exactly **on** a limit, and which **one step past** it?
