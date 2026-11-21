## Approach

```python
def assign(self, user_id, *, is_member, open_count, limit=3):
    if not is_member:
        raise RuleViolation("assignee is not a member of this project")
    if self.is_open and user_id != self.assignee_id and open_count >= limit:
        raise RuleViolation(f"assignee already has {limit} open tasks")
    self.assignee_id = user_id

def _move(self, expected, target):
    if self.status != expected:
        raise RuleViolation(f"cannot move from {self.status} to {target}")

def reopen(self, open_count, limit=3):
    self._move("done", "todo")
    if self.assignee_id is not None and open_count >= limit:
        raise RuleViolation(f"assignee already has {limit} open tasks")
    self.status, self.completed_at = "todo", None
```

The key design question (chapter 8.2): **where do the facts come from?** "At most 3 open tasks" is a rule about the *task*, but the count is a fact that lives in the database. The domain object never calls the database (it would drag SQL back in); the service looks the facts up and passes them as arguments, and the task decides. That keeps the domain pure. A product owner can read this class and check it against the rules of section 2.1, and every rule is tested with **no set-up at all** (chapter 8.5).

## Cost

No new infrastructure: methods on an existing class. The cost is the discipline of passing facts in, and a service that becomes a short **director** (fetch the facts, tell the task to change, save), as chapter 8.4 shows.

## Another way

Keep the rules in the service with `if` statements (p004). That is fine while the rules are few; move them next to the data when they are scattered over several functions and testing them needs a unit of work. A common beginner trap is the **anemic domain model** (classes with only fields and all behaviour in "manager" classes): not wrong everywhere, but when the rules grow, moving them next to the data pays off (chapter 8.6).
