## Approach

Checked by running p018's reference `load` on exactly these inputs:

| Setting | default | file | env | flag | Final |
|---|---|---|---|---|---|
| folder | `~/Downloads` | `/data/inbox` | empty, not set | - | `/data/inbox` (file) |
| keep_days | 30 | 14 | `"7"` | `None` | `7` (env) |
| dry_run | True | false | `off` | `True` | `True` (flag) |
| log_level | WARNING | `info` | (`TIDY_LOGLEVEL` is not read) | `None` | `INFO` (file) |
| api_token | None | ignored | not set | - | `None` (default) |

The answers to the questions. The misspelt `TIDY_LOGLEVEL=DEBUG` was meant to take effect; `load` reads `TIDY_LOG_LEVEL` (with the underscore), so it is silently ignored. `load` reports unknown keys in the **file**, not unknown environment variables; a stricter loader could warn about any `TIDY_*` variable it does not know, and `settings.sources["log_level"] == "file"` in a debug log line would show the problem at once. `TIDY_DRY_RUN=off` loses to the `--dry-run` flag in the crontab line: flags are the strongest layer, so the job keeps doing dry runs until the flag is removed from the command.

## Cost

Reading only. The habit: when a setting surprises you, print `settings.sources` (never the token) before changing any value.

## Another way

Run it: copy p018's reference, build the same file, `env` dict and `flags`, and print each value with its source. Do it after predicting, to check yourself.
