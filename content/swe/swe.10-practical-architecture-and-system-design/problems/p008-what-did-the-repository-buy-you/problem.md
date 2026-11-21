# What did the repository buy you?

Chapter sections 3.4 (the pain log), 6.4 (so what did the repository buy us? An honest list) and "Try it: the repository for a one-table app". This is the first outcome of the module: **explain what concrete pain a repository layer removes in your own project.** A teammate says: "We added a repository because it is clean architecture, and now we can switch databases whenever we like."

In `answer.md` explain (about 250 to 400 words):

1. **The concrete pains** the repository removed in Taskboard, each with the evidence you could show (pain log rows P3 and P4 of the chapter). Name at least two.
2. **What it did not buy.** Take the teammate's claim about switching databases and say how true it is. Take "faster tests": how much faster, and why is the answer different for SQLite than for PostgreSQL?
3. **What it cost** (name three costs from chapter 1.5 or 6.4).
4. **The danger of fakes** and the tool that keeps them honest.
5. **When to skip it:** an app has one table `notes(id, text)` and three routes (create, read, delete) and no rules. Give a three-line argument. What would make you add the repository later?

Use the words *pain*, *evidence*, *fake*, *contract test*, *mapping*.

## Example

A good sentence for part 1: "Rules and SQL were one block (16 `conn.execute` calls in `main.py`), so a rule could not be read or tested without a database; the repository moved all SQL into one file and let the service ask in business words."
