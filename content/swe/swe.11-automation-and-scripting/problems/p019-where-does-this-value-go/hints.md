## Hint 1

Take one setting at a time and walk the four layers from weakest to strongest, crossing out values that do not count: an empty environment value, a flag that is `None`, an environment variable whose **name** is not exactly `TIDY_` plus the setting name in capitals. The last value that counts wins.

## Hint 2

`folder`: file says `/data/inbox`; `TIDY_FOLDER` is empty (not set); no flag. `keep_days`: file 14, env `"7"` (converted to 7), flag `None`. `dry_run`: file `false`, env `off`, flag `True` (typed). `log_level`: is `TIDY_LOGLEVEL` the variable `load` reads? `api_token`: where is the only place it may come from?
