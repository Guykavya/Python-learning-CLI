## Approach

The model answer is in `answer.md`. A privacy review follows the data: every copy of personal
data or of a secret is a place it can leak from, so the review asks for each copy *who can read it,
for how long, and do they need it*. The best fix removes the copy (do not log it, do not export
it, delete it after N days); the second best restricts who can read it.

## Check your answer

- Did you find the hard-coded token and say that deleting the line is not enough (git history), so the token must be **rotated**?
- Did you notice that the DEBUG line logs the `Authorization` header, so the token also lands in the log file?
- Did you flag that full order JSON (emails) goes into a shared log, and say what to log instead (ids, counts, run id)?
- Did you say that with SQLite the **file permissions** are the access control, and that the raw database must not be in a folder everyone can read?
- Did you replace the marketing export by an aggregate per city with no personal data (data minimisation)?
- Did you give a retention rule instead of "keep forever"?
- For part 3, did you explain *why* the half-fix fails (dictionary attack on sha256, masked rows are still row-level data, a hidden folder is still readable)?
- Did each problem name a concrete group of people who could see the data?

## Another way

You can organise the answer by principle instead of by line: **minimise** (collect, keep and share
only what the question needs: the export and the logs), **protect** (secrets outside code,
pseudonyms instead of emails, least-privilege file access), **forget** (retention). Any order is fine
as long as every problem has a who and a fix.
