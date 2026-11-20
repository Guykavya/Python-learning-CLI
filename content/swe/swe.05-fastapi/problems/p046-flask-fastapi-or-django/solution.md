## Approach

A framework choice is a **match between needs and strengths**, defended in the open, with the price named. Read each brief for its needs, map them to the comparison table of section 23, and say what you give up.

See `answer.md` for a model answer and a checklist. The short version:

| Brief | Choice | The deciding needs |
|---|---|---|
| Warehouse inventory | Django | an admin for forms, search and permissions; many tables with migrations; a beginner team |
| Real-time task API | FastAPI | ASGI and async, WebSockets, Pydantic validation, generated OpenAPI for the mobile client |
| Laptop form | Flask | the developer's skills and the company's existing Flask apps; smallest thing to maintain |

Example of defending with a trade-off: "FastAPI, because ... ; the price is that we wire SQLAlchemy, Alembic and JWT ourselves" is stronger than "FastAPI is the fastest", which is a claim about benchmarks that rarely decides a real project.

## Complexity

Not applicable.

## Another way

Other defensible answers exist if you argue them. Brief 2 with **Django + Channels + DRF** is possible (async views, WebSockets through Channels, OpenAPI through a DRF add-on) when the team already knows Django; you trade FastAPI's type-driven validation for Django's ecosystem. Brief 1 with FastAPI plus a separate admin package is possible but is more work for a beginner team. Brief 3 in Django would work too; it is just more framework than two days and one maintainer need.
