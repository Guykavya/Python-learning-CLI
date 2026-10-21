See the model answer shown when you check. The ideas that must appear:

1. Red: write a small test that fails for the right reason; green: write the least code that passes; refactor: tidy while the tests stay green. A test that never failed might not test anything.
2. Benefits: the tests define the goal and keep you from over-building; every line of code exists because a test needed it; the function is easy to test. Cost: you must know the interface up front and it feels slower at first.
3. The test copies the code's behaviour, not the specification: a bug becomes the "expected" result.
4. First write a failing test that reproduces the bug (red), then fix (green); the test stays as protection against regression.
5. Throw-away scripts, fast experiments, and things hard to check automatically (looks of a screen, real hardware); also tests cannot prove absence of bugs.
