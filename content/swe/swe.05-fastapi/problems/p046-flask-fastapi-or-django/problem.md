# Flask, FastAPI or Django?

Chapter section 23 (the comparison table), with sections 1.1 (ASGI and WSGI), 6 (validation), 15 (WebSockets) and 19 (OpenAPI). You will be asked "which framework would you use?" in interviews and in real teams. There is no single right answer; there is a **defended** answer that names the needs of the project and the trade-off you accept.

Here are three project briefs. For **each** one, in `answer.md`, choose Flask, FastAPI or Django and defend the choice in about 80 to 150 words. Name at least two concrete needs of the brief that your choice serves, and one thing you give up or must add yourself.

1. **Inventory for a small warehouse company.** About 30 database tables (products, suppliers, stock movements, orders). Office staff will spend all day adding and editing records in forms, with search, filters and permissions per role. The two developers know Python but have never built a web app; the owner wants something usable within weeks. No mobile app, no real-time needs.
2. **Real-time task API.** A JSON API for a React web app and a mobile app. Thousands of users keep a board open; when a teammate moves a task, everyone on the team must see it within a second. Many endpoints wait on other services (a notification service, a search service). The mobile team wants an accurate, always up-to-date API description to generate their client code. The backend team is comfortable with type hints and `async`.
3. **A small internal form tool.** One page where employees request a laptop: a form with five fields, an email to IT, and a list page for the IT team. About 20 users. One developer who knows Flask well will build it in two days and must maintain it alone for years. The company already runs two other Flask apps with the same login setup.

Finish with **two or three sentences** on what transfers between the three frameworks whichever one you choose.

A good answer uses the words *async* / *ASGI*, *admin*, *validation*, *OpenAPI*, *ecosystem* and talks about the *team*.
