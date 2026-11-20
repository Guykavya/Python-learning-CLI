# What will the flush do?

Chapter section 9.5. A `Session` collects your changes and writes them at **flush** time (before a query, or at `commit`). Until then it knows what it **will** do: `session.new` (objects added), `session.dirty` (loaded objects that were modified) and `session.deleted` (objects marked for deletion).

`solution.py` has a `Customer(id, name)` model. Write

```python
pending(session)
```

returning `{"new": [...], "dirty": [...], "deleted": [...]}`, each list holding the **names** (`customer.name`) of the objects in that state, **sorted**.

- After `session.add(Customer(name="Asha"))`, `"Asha"` is in `new` (and in nothing else).
- After `flush()`, new objects are no longer new.
- After you change `customer.name` to another value, that customer is in `dirty` (until the flush).
- After `session.delete(customer)`, it is in `deleted` (until the flush).

## Example

```python
s.add(Customer(name="Asha")); pending(s)        # {"new": ["Asha"], "dirty": [], "deleted": []}
s.flush();                    pending(s)        # {"new": [], "dirty": [], "deleted": []}
```
