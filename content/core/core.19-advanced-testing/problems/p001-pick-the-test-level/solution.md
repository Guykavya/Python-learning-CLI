## Approach

Match the **question** to the smallest test that can answer it. If a unit test can answer the
question, use it: it is faster and points at the exact bug.

## Answer

See `answer.md`. In short: 1 unit, 2 integration (tmp_path), 3 unit (fake gateway), 4 e2e,
5 integration (`main(argv)` + tmp_path), 6 real-service integration/contract test, run apart
from the fast suite.

## Cost

Rough cost per test: unit about 1 ms, integration about 10 ms to 1 s, e2e many seconds. A
suite of 500 units, 40 integration and 5 e2e tests runs in well under a minute, and a suite
of 500 e2e tests would take hours.

## Another way

Some teams talk about a "testing trophy" (more integration tests, fewer units). The principle is
the same: choose the cheapest level that gives you real confidence.
