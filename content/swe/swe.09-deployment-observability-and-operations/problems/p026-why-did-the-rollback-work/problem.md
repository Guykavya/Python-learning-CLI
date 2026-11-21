# Why did the rollback work?

Chapter sections 12.3 (automatic rollback), 12.4 (rollback and the database) and "Try it: roll forward or back?". Rolling back **code** is easy because code is stateless. The **database** is not: a migration changed it, and going back to the old code means old code meeting a new schema. The chapter's rule (expand and contract): a migration that only **adds** something (a nullable column) is safe for the old code; one that **renames or drops** something is not, and then you must **roll forward** with a fix.

The program models five deployments. Each release needs some columns (`needs`) and its migration adds or renames columns. A deployment runs the migration first, **and a rollback never undoes a migration**. If the new release is unhealthy, the pointer stays on the previous version. After each step the program says which version is live and whether that version **works** with the schema as it is now.

```python
# What each release needs from the database, and what its migration does to it.
RELEASES = {
    "1.0":   {"needs": {"item", "quantity"},        "adds": set(),   "renames": {}},
    "1.1":   {"needs": {"item", "quantity"},        "adds": {"note"}, "renames": {}},                    # additive
    "1.2":   {"needs": {"item", "qty"},             "adds": set(),   "renames": {"quantity": "qty"}},    # destructive
    "1.2.1": {"needs": {"item", "qty"},             "adds": set(),   "renames": {}},
    "1.3":   {"needs": {"item", "qty", "tag"},      "adds": {"tag"}, "renames": {}},
}


def deploy(state, version, healthy):
    """Run the migration first (it is NEVER undone), then start the release. An unhealthy release is rolled back."""
    release = RELEASES[version]
    state["schema"] |= release["adds"]
    for old, new in release["renames"].items():
        state["schema"].discard(old)
        state["schema"].add(new)
    if healthy:
        state["live"] = version                          # otherwise the pointer stays on the previous version


def report(step, version, healthy, state):
    live = state["live"]
    missing = sorted(RELEASES[live]["needs"] - state["schema"])
    works = "yes" if not missing else "NO, missing " + ",".join(missing)
    verdict = "healthy" if healthy else "unhealthy"
    print(f"{step}. deploy {version} ({verdict}): live={live} schema={','.join(sorted(state['schema']))} live version works: {works}")
    return not missing


state = {"schema": {"item", "quantity"}, "live": None}
broken_after = []
for step, (version, healthy) in enumerate([("1.0", True), ("1.1", True), ("1.2", False), ("1.2.1", True), ("1.3", False)], start=1):
    deploy(state, version, healthy)
    if not report(step, version, healthy, state):
        broken_after.append(step)
print("rolling back was not enough after steps:", broken_after)
```

## What to write

The exact output: six lines (five steps and the final summary line). Work through the steps with a small table of two columns: the schema, and the live version.

## Example

Step 1 deploys `1.0` onto the schema `{item, quantity}`, which it needs: `1. deploy 1.0 (healthy): live=1.0 schema=item,quantity live version works: yes`.

## After you answer

- Step 3 was an **automatic rollback** that "worked" (the pointer is back on 1.1) and still left the service broken. What should the team do next, and why is step 4 a *roll forward*?
- Which kind of migration makes step 5 safe, and how would you have written release 1.2 (expand and contract) so that its rollback was safe too?
