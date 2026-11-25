# Notebook or script?

Chapter section 4. A notebook is best for **looking**, a script or module is best for **repeating**. For each of the six tasks below, write in `answer.md` whether you would use a **notebook**, a **script/module**, or **notebook first, then a module**, and **why**, in one or two sentences each (about 200 to 350 words in all).

1. Explore a CSV you have never seen, to learn what columns and problems it has.
2. A report that must be rebuilt every night at 02:00 from the new data.
3. A parser for messy price strings that three other analyses will reuse.
4. A chart you will walk through with your manager in a meeting.
5. A function `describe(values)` that must be tested with `pytest`.
6. A one-off check: "does this column have duplicate ids?"

Use these words somewhere in your answer: *hidden state*, *run top to bottom*, *import from a module*, *tests*, *version control diff*.

## Example

"A nightly report is a **script**: nobody is there to press Run, and it must give the same answer every night, so it must not depend on *hidden state* from cells run in some old order."
