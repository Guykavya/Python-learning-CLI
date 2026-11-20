# Authentication is not authorisation

Chapter sections 1.2 (words you must use exactly) and 1.4 (six questions for every endpoint). Mixing up these words is the root of many real bugs: an endpoint that checks "is there a valid token?" and then returns **anyone's** order.

In `answer.md` write a clear explanation (about 150 to 300 words) that covers:

1. **Define** identification, authentication and authorisation in one sentence each, and say how they differ. Use one concrete example for each, taken from a shop API (for example `POST /login`, `GET /orders/5`, `DELETE /orders/5`).
2. **Explain accountability:** what must the system record so that, later, somebody can be held responsible for an action, and which of the three words above does it depend on?
3. **Show the bug that comes from confusing them:** describe an endpoint that does authentication but no authorisation, and what a logged-in user can do to it.
4. **List the six questions** of chapter 1.4 that you ask for every endpoint, in a few words each, and say which two of them are the authentication and authorisation questions.

A good answer uses the words *prove*, *allowed*, *owner*, *identity*, *audit log*, *deny by default*.

## After you answer

Compare with `answer.md` and tick the checklist. Then take one endpoint from your own project and write the answer to question 1 and 2 of chapter 1.4 for it.
