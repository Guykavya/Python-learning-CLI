## Model answer

1. **Explore a new CSV: notebook.** You want to look at output after every small step, and a mistake costs nothing. The risk is *hidden state*, so before you trust a number, restart and *run top to bottom*.
2. **Nightly report: script.** A scheduler runs it without a person. A script always starts from a clean process and runs from the first line to the last, so the result does not depend on the order cells were clicked. It also logs failures with an exit code.
3. **Reusable parser: module.** Three analyses must *import from a module*; nobody can import a function from a cell. Put it in `cleaning.py`, give it *tests*, and call it from notebooks.
4. **Chart for a meeting: notebook.** Text, code and picture live together and the audience sees the evidence. Strip or re-run the outputs first so the page matches the code (see p005 and p006).
5. **`describe(values)` with pytest: module.** *Tests* import the function, run in a fresh process and need no kernel. A function that exists only in a cell cannot be tested automatically.
6. **One-off duplicate check: notebook (or a REPL).** It will run once and the answer is a single number. Do not over-engineer; if it turns out to be needed every week, promote it to a script.

A pattern runs through all six: explore in a notebook, then move what must be repeated, tested or shared into a module and import it. The *version control diff* of a `.py` file shows exactly which line changed; a notebook's JSON also contains outputs and counters, which is noise.

**Checklist: your answer should mention**
- [ ] a verdict and a reason for each of the six tasks
- [ ] hidden state, and the habit of restarting and running top to bottom
- [ ] that reusable or tested code lives in a module you import
- [ ] that scheduled jobs are scripts
- [ ] that notebooks make noisy version-control diffs
- [ ] "notebook first, then extract" as the usual workflow
