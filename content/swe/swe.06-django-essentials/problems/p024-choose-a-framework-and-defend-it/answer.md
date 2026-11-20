## Model answer

**B: public API, ML calls, 500 concurrent clients.** Choose **FastAPI**. The user is another program (the mobile app), there is no admin, no forms and no templates, and the work is mostly *waiting* for the ML service. `async` endpoints with an async HTTP client let one process hold hundreds of waiting requests, and Pydantic validation and the automatic OpenAPI docs come with the framework. Cost: we build authentication, migrations and any data screens ourselves, and we must never call blocking code inside an `async def`. Trigger: if measurements show the ML service or the database, not the framework, is the limit, the choice does not matter and we keep it; if the team already runs Django and needs its admin for the same data, Django REST Framework with more workers is also fine.

**D: content site with accounts, comments and moderators.** Choose **Django**. The users are people in browsers and staff, and the data model is the heart: articles, comments, users, groups with permissions. Django gives templates and forms (with escaping and CSRF), authentication, permissions for the moderator role, the admin as the editor and moderation screen, and an ORM with migrations. It is server-rendered, which also suits search engines. Cost: it is heavier than a micro-framework and async is not its strength, and we follow Django's conventions. Trigger: if the front end becomes a single-page app, the site turns into an API job and DRF (or FastAPI) takes over the data part.

**G: live notifications for an existing Django shop.** **Keep Django** and add the real-time part: Channels, or a small separate FastAPI service that pushes the notifications. Rewriting 30,000 lines of tested code for one feature costs far more than it gives, and the shop's admin, ORM and permissions keep working. Cost: two moving parts to run and secure, and the two must agree on data (same database, or calls over HTTP). Trigger: if the live part grows to be most of the product, or measurements show Django workers cannot hold the open connections, move more traffic to the async service.

**Checklist: your answer should mention**
- [ ] B: the user is a program; the work is mostly waiting, so async fits; validation and docs come built in
- [ ] B: the cost (you build auth, admin and migrations; do not block the event loop)
- [ ] D: people and staff are the users; the data model, permissions and the admin are central
- [ ] D: templates, forms, CSRF and authentication come built in
- [ ] D: the cost (heavier, conventions, async not the strength) and a trigger (a single-page front end makes it an API job)
- [ ] G: do not rewrite working, tested code for one feature; add Channels or a small side service
- [ ] G: the cost (two parts to run) and a trigger (the live part becomes most of the product)
- [ ] every job has a choice, a cost **and** a trigger to revisit
- [ ] no weak reasons ("it is faster" with no measurement, "everyone uses it", "it is newer")
