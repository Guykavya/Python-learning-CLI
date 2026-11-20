## Hint 1

For each brief, underline the **needs**: who uses it (staff in forms? other programs through JSON?), whether many connections wait at once, whether something must be pushed in real time, who maintains it and what they already know, and what already exists in the company. Then read the table of section 23 row by row and see which column serves those needs.

## Hint 2

Ask three questions per brief: (1) Is it mainly **HTML forms for people** or a **JSON API for programs**? (2) Does it need **async** (many slow waits, WebSockets)? (3) What does the **team** know, and what already runs in the company? Django wins (1) with its admin; FastAPI wins (2); (3) often decides small projects.

## Hint 3

```text
1  forms + permissions all day, beginners  -> Django (admin, ORM, migrations, conventions); give up: weight, opinions
2  JSON for two clients, real-time, waits  -> FastAPI (ASGI, WebSockets, Pydantic, OpenAPI); give up: build admin/auth/ORM wiring yourself
3  tiny, one Flask developer, Flask in house -> Flask (skills, shared login, least to maintain); give up: little, unless it grows
transfers: HTTP, validation, sessions, auth, tests
```
