## Model answer

**Pains removed (with evidence).**
- **P3, testing one rule needs the whole stack.** Checking "the 4th open task is refused" needed an HTTP client, JSON, a temporary database file and four requests (about 3.8 ms each in the chapter's measurement, thousands of times slower than a function call). With a **fake** repository the same rule runs as a plain function call: seven unit tests, no SQL, no files.
- **P4, rules and SQL were one block.** `main.py` had 16 `conn.execute` calls mixed with 8 `raise HTTPException`. After the repository, all SQL is in one file and the service reads like the rules of section 2.1 (`repos.tasks.open_count(user_id) >= MAX_OPEN`), in business words.

**What it did not buy.**
- **"We can switch databases."** Only partly true. The *work* is localised (one file), but you still write and test every method, and SQL dialects differ. Switching databases is also rarely real. Speculation is not a pain (chapter 1.4 "Try it").
- **"Faster tests."** Only a little with SQLite: an in-memory SQLite database is already a very good test double (the chapter measured about the same speed as the fake). The fake wins when the real database is slow to start (PostgreSQL, a remote service) or when you want to inject failures that are hard to trigger in SQL.
- **"It is free."** No.

**What it costs.** More files and names (`repo.py`, a fake, a `Task` object); one more jump when reading ("where does `get_task` run SQL?"); **mapping** code (rows in, objects out, objects in, rows out); and the risk that the **fake lies**. In Taskboard: one file of about 90 lines, a fake of about 80 lines and a contract test.

**Fakes can lie.** A real database returns a **new** object on every `get`; a lazy fake that returns the same object hides the bug "I changed the task and forgot to save". The tool is the **contract test**: one set of tests for the repository interface that runs against the SQL repository **and** the fake. If both pass, they agree (and a contract test is itself tested by feeding it a deliberately lying fake, as in p007).

**When to skip it.** The `notes` app has no rules for a service to hold (no P1), three one-line SQL statements (no P4) and tests through the route with a temporary database are easy (no P3). The repository would be a mapping layer with nothing to protect. Add it when a **rule** appears ("a user may have at most 100 notes") or when the same query is copied into several routes. No pain, no layer.

**Checklist: your answer should mention**
- [ ] at least two concrete pains with evidence (tests needing HTTP and a database; rules and SQL mixed, with numbers)
- [ ] switching databases is only partly true and rarely real; the work is localised but not free
- [ ] "faster tests" depends on the database: small for in-memory SQLite, large for a slow or remote database
- [ ] costs: more files, extra jump when reading, mapping code, fakes that can lie
- [ ] contract tests keep fakes honest, running the same tests against both implementations
- [ ] skip it for a one-table app with no rules; add it when a rule or a copied query appears
