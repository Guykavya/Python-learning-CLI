# Two dispatchers at once

Chapter sections 9.5 (the dispatcher and the handlers) and "Try it: what if two dispatchers run at once?". The outbox holds events that must be delivered ("tell Ana that a task was assigned"). A **dispatcher** reads the pending items and delivers each one: send the e-mail, then mark the item sent. Now two dispatcher processes, `D1` and `D2`, run at the same time on the same outbox.

The program below replays **one fixed interleaving** of their steps (the `script` list; each dispatcher handles the items it has read, one per `next` step). Three runs:

1. **no claim**: a dispatcher simply sends and marks;
2. **with a claim**: before sending, a dispatcher *claims* the item with one atomic operation (`UPDATE outbox SET claimed_by = ? WHERE id = ? AND claimed_by IS NULL`, here: if `claimed_by` is already set, skip the item);
3. **with a claim, and `D1` dies after claiming item 2** (the process is killed before it sends); the claim has **no expiry** in this model.

```python
USERS = ["ana", "ben", "cy"]                       # outbox items 1, 2, 3: "tell this user a task was assigned"


def run(use_claim, d1_crashes_after_claiming_item=None):
    outbox = {i: {"user": u, "claimed_by": None, "sent": False} for i, u in enumerate(USERS, start=1)}
    mails = {u: 0 for u in USERS}
    todo = {"D1": [], "D2": []}                    # the items each dispatcher read and still has to handle
    alive = {"D1": True, "D2": True}

    def step(who, what):
        if not alive[who]:
            return
        if what == "read":
            todo[who] = [i for i, row in outbox.items() if not row["sent"]]        # read the pending items
            return
        if not todo[who]:
            return
        item = todo[who].pop(0)                    # next item of my list
        row = outbox[item]
        if use_claim:
            if row["claimed_by"] is not None:      # somebody claimed it first: skip it
                return
            row["claimed_by"] = who                # the claim: one atomic UPDATE ... WHERE claimed_by IS NULL
            if item == d1_crashes_after_claiming_item and who == "D1":
                alive[who] = False                 # the process dies before it sends
                return
        mails[row["user"]] += 1                    # send the e-mail
        row["sent"] = True                         # mark it sent

    script = [("D1", "read"), ("D1", "next"), ("D2", "read"), ("D1", "next"), ("D2", "next"), ("D1", "next"), ("D2", "next")]
    for who, what in script:
        step(who, what)
    return mails


def show(label, mails):
    print(f"{label:34}" + " ".join(f"{user}={n}" for user, n in mails.items()))


show("no claim:", run(use_claim=False))
show("with a claim:", run(use_claim=True))
show("claim, D1 dies after claiming 2:", run(use_claim=True, d1_crashes_after_claiming_item=2))
```

## What to write

The exact output: three lines. Count, for each user, how many e-mails were sent. The step order matters: a dispatcher **reads** its list of pending items at its `read` step, and an item that was already **sent** at that moment is not in its list.

## Example

In the first run `D1` reads `[1, 2, 3]`, sends item 1 (Ana) and marks it sent. When `D2` reads, item 1 is no longer pending, so `D2` has `[2, 3]`. Think about what `D1` and `D2` do with items 2 and 3 next.

## After you answer

- Why did the idempotency key of chapter 9.5 still protect the *e-mail* in the first run, even though the work was done twice?
- What does the third run show about a claim that **never expires**, and what would you add (swe.08's `lease`)?
