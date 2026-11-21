## Hint 1

Compare the route above with what a service function may know. Which lines are about HTTP (`HTTPException`, status codes, `body`) and which are about the rules of Taskboard? Move only the second kind, and turn each `HTTPException` into the domain error with the same meaning. Which line must **not** move: the one that ends the transaction?

## Hint 2

```text
title = title.strip(); bad length -> InvalidInput
project missing -> NotFound
if assignee: not a member -> RuleViolation; open tasks >= MAX_OPEN -> RuleViolation(f"assignee already has {MAX_OPEN} open tasks")
insert the task, insert the audit line 'created'
if assignee: mailer.send_email(email, f"New task: {title}")
return {"id": ..., "title": title, "status": "todo", "assignee_id": assignee_id}     (no commit)
```
