## Hint 1

A `with` statement calls `__enter__` at the start and `__exit__` at the end, **also when an exception flew out of the block**. What does that give you for free that a `try/except` in every use case would have to repeat? Which call undoes uncommitted work, and is it harmful when nothing is uncommitted?

## Hint 2

```text
__enter__: self.conn = connect(self.path); repos = SqliteRepos(self.conn)
           self.tasks, self.projects, self.users = repos.tasks, repos.projects, repos.users; return self
__exit__:  self.conn.rollback(); self.conn.close()        # always; no return value, so exceptions propagate
commit:    self.conn.commit()
```
