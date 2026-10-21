**1. Red, green, refactor.** *Red*: write one small test for a behaviour that does not exist
yet, run it, and watch it fail. For `slugify` the first test is `assert slugify("Hello") == "hello"`.
*Green*: write the least code that makes it pass (`return text.lower()`), nothing more. *Refactor*:
clean the code while the tests stay green. Then the next test: `"Hello World"` should give
`"hello-world"`: red again, so I add `split` and `join`. The test must fail first, because a test
that has never failed may be unable to fail: it might have no assert, or test the wrong thing.
Seeing red proves the test can detect the missing feature.

**2. Benefits and a cost.** (a) The test is the **specification** I wrote before I was biased by my
own code, so it states what the function should do, not what it happens to do. (b) I only write
code that a test needs, so the code stays small, and every line is covered. The function also ends
up easy to test, because I designed the call first. A cost: I must decide the function's name,
arguments and result before writing it, which is hard when I do not yet understand the problem; and
it feels slower at the start.

**3. Test after by copying the output.** If the function has a bug and I paste its output into the
`assert`, the test now *promises* the bug is correct. The test passes forever and says nothing about
what the function should do: there is no independent **specification**. When someone later fixes
the bug, the test fails and looks as if the fix broke something. Expected values must be worked out
from the requirements, by hand, not from the code.

**4. A bug report with all tests green.** First **reproduce** the bug in a new test: write the test
that expresses the correct behaviour and watch it fail (red). Only then fix the code until it
is green. The test stays in the suite, so the bug can never come back unnoticed: that protection is
what a **regression** test is. Fixing first and testing afterwards loses the proof that the test
could have caught the bug.

**5. When tests are not worth it, or not enough.** A throw-away script I will run once, or a quick
experiment to learn how a library behaves, is not worth a suite. Some things are hard to check
automatically: how a page looks, a real printer or camera, timing on a slow network (they need
manual or special tests). And no number of tests proves there are no bugs: tests only show the
cases I tried work.
