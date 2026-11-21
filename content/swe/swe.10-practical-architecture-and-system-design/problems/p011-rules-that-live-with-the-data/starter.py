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

    # TODO: assign, start, pause, finish, reopen
