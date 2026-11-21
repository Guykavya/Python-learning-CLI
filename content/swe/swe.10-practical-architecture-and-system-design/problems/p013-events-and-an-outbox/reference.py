import copy
from dataclasses import asdict, dataclass, field, replace

MAX_OPEN = 3


class DomainError(Exception):
    pass


class NotFound(DomainError):
    pass


class RuleViolation(DomainError):
    pass


@dataclass(frozen=True)
class TaskAssigned:
    assignee_id: int
    title: str


@dataclass
class Task:
    id: int | None
    project_id: int
    title: str
    status: str
    assignee_id: int | None
    created_at: str
    completed_at: str | None = None
    events: list = field(default_factory=list, repr=False, compare=False)

    def __copy__(self):
        return replace(self, events=[])             # a stored copy must never share pending events

    @property
    def is_open(self):
        return self.status != "done"

    def assign(self, user_id, *, is_member, open_count):
        if not is_member:
            raise RuleViolation("assignee is not a member of this project")
        if self.is_open and user_id != self.assignee_id and open_count >= MAX_OPEN:
            raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")
        self.assignee_id = user_id
        self.events.append(TaskAssigned(user_id, self.title))


def drain_events(task):
    """Take the task's pending events out, as (kind, payload) pairs ready to store."""
    pending, task.events = task.events, []
    return [(type(e).__name__, {"task_id": task.id, **asdict(e)}) for e in pending]


def assign_task(uow, task_id, user_id, now):
    with uow:
        task = uow.tasks.get(task_id)
        task.assign(user_id,
                    is_member=uow.projects.is_member(task.project_id, user_id),
                    open_count=uow.tasks.open_count_for(user_id))
        uow.tasks.save(task)
        for kind, payload in drain_events(task):          # the intention is saved in the SAME transaction
            uow.outbox.add(kind, payload, now)
        uow.commit()
        return task


def dispatch(new_uow, handlers, now, limit=50):
    with new_uow() as uow:
        items = uow.outbox.pending(limit)
    delivered = failed = 0
    for item in items:
        try:
            with new_uow() as uow:                        # one transaction per item: one bad item cannot block the others
                handler = handlers.get(item.kind)
                if handler is not None:
                    handler(uow, item)
                uow.outbox.mark_sent(item.id, now)
                uow.commit()
            delivered += 1
        except Exception:
            failed += 1                                    # nothing of this item was saved: it stays pending
    return delivered, failed
