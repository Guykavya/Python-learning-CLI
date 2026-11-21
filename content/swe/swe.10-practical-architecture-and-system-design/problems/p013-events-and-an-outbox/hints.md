## Hint 1

Which two writes must succeed or fail **together**? Put both between `with uow:` and **one** `uow.commit()`. Then ask who may send the e-mail, and when: not the use case. The dispatcher is a second program that only reads the outbox; what must be true of each delivery so that one failure cannot block the others?

## Hint 2

```text
assign_task: with uow: task = uow.tasks.get(id); task.assign(user, is_member=..., open_count=...); uow.tasks.save(task)
             for kind, payload in drain_events(task): uow.outbox.add(kind, payload, now)
             uow.commit(); return task
dispatch:    with new_uow() as uow: items = uow.outbox.pending(limit)
             for item in items:
                 try: with new_uow() as uow: handler = handlers.get(item.kind); handler(uow, item) if there is one
                                             uow.outbox.mark_sent(item.id, now); uow.commit(); delivered += 1
                 except Exception: failed += 1        # the item stays pending; carry on
```
