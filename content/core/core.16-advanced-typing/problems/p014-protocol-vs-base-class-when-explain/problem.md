# Explain: Protocol or base class?

You are designing a small reporting library. Two parts need an interface.

**Part 1: exporters.** Your library calls `exporter.export(rows) -> str`. Users of the library
write their own exporters. Many want to reuse a CSV exporter from a third-party package that
they cannot change. Some of your users are in other teams who do not import your package at all
in their own code.

**Part 2: storage backends.** Inside your library there are three storage classes (memory,
disk, S3). They all need the same helper code: a `save` method that validates the data, then
calls a method `_write(data)` that each backend implements. A backend that forgets `_write`
must fail as early as possible, at the moment it is created.

In `answer.md` (about 200 to 350 words), explain:

1. What is the difference between **nominal** and **structural** typing? Which one is a
   `Protocol` and which one is a normal base class (or `ABC`)?
2. Which would you use for Part 1, and which for Part 2? Give the reasons from the text above.
3. What do you lose if you use a Protocol for Part 2? What do you lose if you use an ABC for
   Part 1?
4. A friend says "Protocols make `isinstance` checks unnecessary". Is that right? What does
   `@runtime_checkable` give you, and what does it **not** check?
