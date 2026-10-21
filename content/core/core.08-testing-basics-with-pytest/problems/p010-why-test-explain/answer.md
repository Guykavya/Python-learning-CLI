**1. What a test is.** An automated test is a small function that calls my code with a chosen
**input**, states the **expected output** I worked out beforehand, and uses an **assert** to compare
the two. If they differ, the test fails and says so. A person does not have to look at anything:
the computer decides pass or fail.

**2. Why two REPL tries, or hand testing, are not enough.**
- Two tries cover two cases. Bugs usually live at the edges: a discount of 0, a discount of 100, a
  price of 0, a negative number. Nobody remembers to try all of them each time.
- A REPL session disappears when I close it. A test file stays, so anyone can repeat the check in
  one second, a month later, on another machine.
- Ravi's hand testing costs more with every new feature: after each change he must repeat every old
  check, and he will skip some. That is how a **regression** gets in: a change that breaks something
  that used to work, found weeks later by a user. A test suite re-runs everything after every change.
- Tests also document what the function is supposed to do, with examples that cannot go out of date.

**3. The cost.** Writing tests takes time, and the tests must be kept up to date when the behaviour
changes on purpose. That time is paid back the first time a test catches a regression in seconds
instead of a user finding it, and it makes changing code less frightening.

**4. What passing does not prove.** A passing suite only proves the code works for the cases the
tests tried. Untested inputs may still be wrong, and a wrong test (a wrong expected value) can pass
a wrong function. Tests reduce risk; they do not prove correctness.
