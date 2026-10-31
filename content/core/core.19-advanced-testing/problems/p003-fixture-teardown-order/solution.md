## Approach


Setup order for `test_one(session, cache)`: `session` is first in the parameter list, but it
needs `db`, so `db` runs first, then `session`, then `cache`. Teardown is the mirror image:
`cache`, `session`, `db`. `test_two` fails at its `assert`, but its fixture still gets torn down
(that is the whole point of `yield` fixtures: cleanup is guaranteed). Because one test failed,
`pytest.main` returns exit code 1.


## Output

```text
open db
start session
fill cache
test_one runs
clear cache
end session
close db
fill cache
test_two runs
clear cache
pytest exit code 1
```
