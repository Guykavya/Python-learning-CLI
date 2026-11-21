## Hint 1

Do it in the order of the pains, one remedy at a time, and run the tests after each step (the chapter's refactoring contract: the outside does not change). First the service layer: move the rules out of the routes into functions that raise domain errors and call `_check_capacity` on **all three** paths. Then give them a repository interface instead of SQL. Then replace the shared connection by one unit of work per request. Last, write the documents from your own pain log.

## Hint 2

```text
SqliteUnitOfWork.__enter__: self.conn = connect(path); self.tasks, self.projects, self.users = repositories on self.conn; return self
SqliteUnitOfWork.__exit__:  self.conn.rollback(); self.conn.close()        commit(): self.conn.commit()
create_task(uow, mailer, project_id, title, assignee_id):  validate the title; with uow: project exists? member? capacity? add task, add audit,
                                                             mail (before commit), uow.commit(); return the task
update_task: with uow: get; assignment (member, capacity unless done or same person, save, audit, mail); status (ALLOWED, capacity when reopening); save; commit
create_app: one exception handler for DomainError; each route = new SqliteUnitOfWork(db_path) + one service call + task_json
```
Order matters for correctness: rules first, writes second, e-mail last, **one** `commit()` at the very end.

## Hint 3

For the documents, copy the structure of the three ADRs of chapter 18.2: Context states the pain **with the failing test as evidence**; Decision says what each layer is responsible for; Consequences has pluses and minuses (more files, mapping code, `commit()` must be called); Alternatives says what you did not do (copy the check into the two routes, a domain model, separate services) and why.
