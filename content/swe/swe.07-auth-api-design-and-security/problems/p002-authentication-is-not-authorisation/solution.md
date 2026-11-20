## Approach

Build the answer in the order of the task: three definitions with one example each, then accountability, then the bug, then the six questions. See `answer.md` for a model answer and a checklist.

The sentence to remember: **authentication proves who you are; authorisation decides what you may do.** Every endpoint needs both, and the second one is the one that gets forgotten, because the first one "works" in every demo.

Example: `GET /orders/5` with a valid token for user 1. Authentication says "this is user 1". Authorisation must still ask "does order 5 belong to user 1?" before answering. If the code only asks the first question, the endpoint is open to every logged-in user.

## Complexity

Not applicable.

## Another way

Explain it with a different picture: a **passport** (authentication) gets you into the country; it does not open every door inside. Or with the code: `current_user = authenticate(request)` is one line, and `policy.allow(current_user, "read", order)` is the other line that must follow it (chapter 7.3).
