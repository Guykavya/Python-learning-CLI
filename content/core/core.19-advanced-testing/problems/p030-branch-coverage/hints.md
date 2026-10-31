## Hint 1

Draw the function as a list of decisions: weight <= 0; weight > 20; weight > 5; zone is abroad; express while abroad; express at home; the loop: skipped, entered,
`FREE`, `HALF`, other code. Each decision needs a call where it goes one way and a call where it goes the other. How many calls do you need at least? (Several decisions can be
settled by the same call.)

## Hint 2

Work out the expected fee by hand for every call and write it into the `assert` (base 500, then weight, then zone, then express, then coupons). Remember the loop has more than
two outcomes: no codes, a code that matches nothing and the loop ends, `FREE`, `HALF` followed by another code. Put borders at 5/6 kg and 20/21 kg too.

```
ValueError:     weight 0 and -3 (pytest.raises)
weights:        3 -> 500, 10 -> 1000, 25 -> 2000; borders 5, 20, 21
zones:          abroad 3 -> 1500, abroad 10 -> 3000, abroad + express -> ValueError, home + express 3 -> 1500
coupons:        ["FREE"] -> 0, ["HALF"] on 1000 -> 500, ["HALF","FREE"] -> 250, ["NOPE"] -> 500, ["NOPE","HALF"], ["NOPE","FREE"]
```
