## Approach

The model answer is in `answer.md`. The test for every migration: **can the previous version of the code still run against the new schema, and can the new version run against the old one?** If both answers are yes, the deploy has no downtime.

## Complexity

Not applicable.

## Another way

Run each migration against a copy of production data and watch the lock time; use a migration linter (such as `squawk` for PostgreSQL) in CI to flag unsafe statements automatically.

## Why it matters

Most migration outages come from one of these six patterns. Learning to recognise them is what separates "it worked in development" from "it works in production".
