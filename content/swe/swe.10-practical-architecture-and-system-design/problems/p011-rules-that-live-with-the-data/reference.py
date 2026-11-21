from dataclasses import dataclass


class DomainError(Exception):
    pass


class RuleViolation(DomainError):
    pass


@dataclass
class Task:
    id: int | None
    project_id: int
    title: str
    status: str
    assignee_id: int | None
    created_at: str
    completed_at: str | None = None

    @property
    def is_open(self):
        return self.status != "done"

    def assign(self, user_id, *, is_member, open_count, limit=3):
        if not is_member:
            raise RuleViolation("assignee is not a member of this project")
        if self.is_open and user_id != self.assignee_id and open_count >= limit:
            raise RuleViolation(f"assignee already has {limit} open tasks")
        self.assignee_id = user_id

    def _move(self, expected, target):
        if self.status != expected:
            raise RuleViolation(f"cannot move from {self.status} to {target}")

    def start(self):
        self._move("todo", "doing")
        self.status = "doing"

    def pause(self):
        self._move("doing", "todo")
        self.status = "todo"

    def finish(self, now):
        self._move("doing", "done")
        self.status, self.completed_at = "done", now

    def reopen(self, open_count, limit=3):
        self._move("done", "todo")
        if self.assignee_id is not None and open_count >= limit:
            raise RuleViolation(f"assignee already has {limit} open tasks")
        self.status, self.completed_at = "todo", None
