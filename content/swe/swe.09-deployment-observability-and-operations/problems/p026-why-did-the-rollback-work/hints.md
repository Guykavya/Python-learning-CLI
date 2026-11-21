## Hint 1

Keep two things in view at every step: the **schema** (a set of column names that only grows or gets renamed, never goes back) and the **live version** (which changes only for a healthy release). After each step test: is `needs` of the live version a subset of the schema?

## Hint 2

Step 3 is the interesting one. The migration of 1.2 already ran (it renamed `quantity` to `qty`), then the release was found unhealthy, so the pointer stays on 1.1. What does 1.1 need? Is it in the schema now? In step 5 the migration adds `tag` and the release fails: does the old live version, 1.2.1, need anything that disappeared?
