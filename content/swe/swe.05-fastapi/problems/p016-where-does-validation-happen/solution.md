## Approach

Answer in the order a request travels: who turns hints into checks, where those checks sit in the lifecycle, what the client sees when they fail, and which failures belong somewhere else.

See `answer.md` for a model answer and a checklist. The key sentence: **type hints describe the API, Pydantic enforces them before your function runs, and a 422 means "the client's data broke those declared rules", nothing more.**

Example: `POST /projects/1/tasks {"title": "ab", "priority": 9}` never reaches `create`; the client gets one 422 with two entries (`["body", "title"]` `string_too_short` and `["body", "priority"]` `less_than_equal`). `POST /users {"username": "asha"}` when `asha` exists passes validation, reaches the endpoint, which looks in the database and raises `HTTPException(409, "username taken")`.

## Complexity

Not applicable.

## Another way

Explain it with a building: security at the gate checks every visitor's ID card against the rules printed on the door (validation, 422 at the gate). The office inside decides whether *this* visitor may book *this* room today, which needs the booking register (business rules, 409/403). And if the lift breaks, that is the building's fault (500), not the visitor's.
