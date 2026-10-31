## Approach


`per_test` is function-scoped, so every test that names it triggers a new setup: `test_a` gets 1,
`test_b` gets 2, `test_c` does not use it at all, and `test_d` gets 3. `per_module` is created by
the first test that needs it (`test_a`), reused by `test_b` and `test_c`, and torn down after the
last test of the module, which is after `test_d`, even though `test_d` never used it. The setup
print of a fixture comes before the test's own print.

Note the order inside `test_a`: its parameters are `(per_test, per_module)`, but pytest always
sets up **wider-scope fixtures first** (session, then module, then class, then function), so
`per_module` runs before `per_test`.


## Output

```text
per_module setup 1
per_test setup 1
a: 1 1
per_test setup 2
b: 2 1
c: 1
per_test setup 3
d: 3
per_module teardown
pytest exit code 0
```
