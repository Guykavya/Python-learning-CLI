# Where does the commit belong?

Chapter sections 7.1, 7.3, 9.1 (the pain, proved) and 9.2 (save the intention, deliver it later), and "Try it: where does the commit belong?". The use case is "assign a task, write its audit line, and e-mail the assignee". There are five ways to arrange the commit and the e-mail, and each one fails differently when something goes wrong. The program below models them with a tiny transactional database (`work` is the open transaction, `saved` is what survives; `rollback()` drops the uncommitted work) and a mailer that either works or is down. **A `Crash` stands for the process dying** (nothing runs after it, and uncommitted work is lost).

```python
class Database:
    """A tiny transactional store. Changes go to `work`; commit() copies them to `saved`, rollback() drops them."""

    def __init__(self):
        self.saved = {"tasks": 0, "audit": 0, "outbox": 0}
        self.work = dict(self.saved)

    def insert(self, table):
        self.work[table] += 1

    def commit(self):
        self.saved = dict(self.work)

    def rollback(self):
        self.work = dict(self.saved)


class Mailer:
    def __init__(self, provider_up):
        self.provider_up, self.sent = provider_up, 0

    def send(self):
        if not self.provider_up:
            raise IOError("provider is down")
        self.sent += 1


class Crash(BaseException):
    """The process dies."""


def v1_send_then_commit(db, mailer):
    db.insert("tasks"); db.insert("audit")
    mailer.send()                                  # fails
    db.commit()


def v2_commit_then_send(db, mailer):
    db.insert("tasks"); db.insert("audit")
    db.commit()
    mailer.send()                                  # fails


def v3_send_then_the_process_dies(db, mailer):
    db.insert("tasks"); db.insert("audit")
    mailer.send()                                  # works
    raise Crash()                                  # before commit
    db.commit()


def v4_repository_commits_each_write(db, mailer):
    db.insert("tasks"); db.commit()                # add() commits "so nobody can forget"
    raise IOError("disk full")                     # the audit write fails
    db.insert("audit"); db.commit()


def v5_outbox(db, mailer):
    db.insert("tasks"); db.insert("audit"); db.insert("outbox")
    db.commit()                                    # task, audit and event are saved together
    # the request is over; the dispatcher runs later and the provider is still down
    try:
        mailer.send()
    except IOError:
        pass


VERSIONS = [("v1", v1_send_then_commit, False), ("v2", v2_commit_then_send, False), ("v3", v3_send_then_the_process_dies, True),
            ("v4", v4_repository_commits_each_write, True), ("v5", v5_outbox, False)]
for name, version, provider_up in VERSIONS:
    db, mailer = Database(), Mailer(provider_up)
    try:
        version(db, mailer)
    except (IOError, Crash):
        db.rollback()                              # whatever was not committed is dropped
    s = db.saved
    half = "yes" if s["tasks"] != s["audit"] else "no"
    print(f"{name}: task_saved={'yes' if s['tasks'] else 'no'} emails_sent={mailer.sent} half_saved={half} outbox_pending={s['outbox']}")
```

Python facts: `except (IOError, Crash)` catches both; after it the program calls `db.rollback()`, which drops the uncommitted work. `IOError` is an alias of `OSError`. The mailer of `v1`, `v2` and `v5` is **down**; the mailer of `v3` and `v4` is **up**.

## What to write

The exact output: five lines. Reason about each version step by step: what is committed at the moment of the failure, and what already left the building?

## Example

Version `v2` inserts the task and the audit line, commits, and then the mailer fails: the data is saved, no e-mail was sent, nothing is half-saved: `v2: task_saved=yes emails_sent=0 half_saved=no outbox_pending=0`.

## After you answer

- Which version sends an e-mail for a change that **never happened**, and which version makes the client retry a request whose data was **already saved** (and create a duplicate)?
- Which version has the guarantee table of chapter 9.2, and what is the price it still pays (at-least-once delivery)?
