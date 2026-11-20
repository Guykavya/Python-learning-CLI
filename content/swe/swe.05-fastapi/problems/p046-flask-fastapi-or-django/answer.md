## Model answer

**1. Warehouse inventory: Django.** The heart of the brief is "staff edit records in forms all day, with search, filters and permissions". Django's built-in **admin** gives exactly that from the model definitions: list pages with search and filters, edit forms with validation, users, groups and per-model permissions, in days instead of weeks. Its ORM and **migrations** handle 30 tables, and the "batteries included" style suits a team that has never built a web app: there is one documented way to do auth, forms and admin, so they make fewer architecture decisions. Nothing here needs async or real-time. What I give up: Django is heavier and more opinionated; if a JSON API is needed later, Django REST Framework adds it.

**2. Real-time task API: FastAPI.** It is a JSON API first, consumed by two front ends, so Django's templates and admin are not the point. FastAPI is **ASGI** and async-first: endpoints that wait on other services can `await` without blocking a worker, and **WebSockets** are built in for the "see it within a second" requirement (with Redis pub/sub when there are several workers). Request **validation** comes from Pydantic models, and the **OpenAPI** document is generated from the code, so the mobile team's generated client is always accurate. The team already knows type hints and async, which FastAPI rewards. What I give up: no admin, no built-in auth or ORM; I choose and wire SQLAlchemy, Alembic and the JWT handling myself.

**3. Laptop request form: Flask.** One form, one list, one email, twenty users: any framework works, so the deciding factors are the **team** and the **existing ecosystem** in the company. The only developer knows Flask, and two Flask apps already share the login setup, so the third one can reuse that code and the deployment knowledge. Flask with a WTForms-style form (or a small hand-written validator) and server-side templates is the least code and the least to maintain alone. No async, no API clients, no admin needed. What I give up: if the tool grows into a big admin app, Django would have been a better start; at this size that risk is small.

**What transfers.** HTTP itself (methods, status codes, headers, cookies), validation at the boundary, dependency-style setup and teardown of resources, ORM sessions and transactions, hashing passwords and token or session authentication, and testing through a test client are the same ideas in all three. Learning one framework well makes the next one a matter of new names for known concepts.

**Checklist: your answer should mention**
- [ ] brief 1: Django, because of the built-in **admin** (forms, search, filters, permissions) and the ORM with migrations
- [ ] brief 1: a beginner **team** benefits from "batteries included" conventions
- [ ] brief 2: FastAPI, because it is **ASGI**/**async** (waiting on other services, many open connections) with built-in **WebSockets**
- [ ] brief 2: Pydantic **validation** and generated **OpenAPI** for the mobile team's client
- [ ] brief 2: the trade-off: no admin or built-in ORM/auth; you choose and wire them
- [ ] brief 3: Flask, because of **team skills** and the existing Flask **ecosystem** (shared login, deployment) in the company
- [ ] brief 3: async is not needed; the smallest thing one person can maintain wins
- [ ] each choice names something given up or added by hand
- [ ] what transfers: HTTP, validation, sessions/transactions, auth, testing
