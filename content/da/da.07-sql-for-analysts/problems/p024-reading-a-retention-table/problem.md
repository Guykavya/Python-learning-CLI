# Reading a retention table

Chapter sections 6.3 to 6.5. A manager sends you this retention matrix from a product dashboard (retention in percent of the
cohort, by month since sign-up) and asks: *"Are newer users better or worse than older users, and what will month 3 look like
for April?"*

| Cohort | Size | M0 | M1 | M2 | M3 |
|---|---|---|---|---|---|
| Jan | 100 | 100 | 60 | 45 | 40 |
| Feb | 120 | 100 | 55 | 42 | |
| Mar | 90 | 100 | 62 | | |
| Apr | 150 | 100 | | | |

The data were extracted at the start of **May** (the April cohort has only its sign-up month).

In `answer.md`, in about 150 to 250 words:

1. Say what a **row** and a **column** of this table mean, and why the bottom-right corner is empty.
2. Explain what you can and cannot conclude about "newer against older" users from this table.
3. Describe how you would build **one pooled retention curve** (a single line "retention by month since sign-up") and why it
   must use only the cells that exist.
4. Say why comparing raw counts of active users between cohorts would mislead.

## Example

A start: "Each row is a cohort: the users who signed up in the same month. Each column is the number of months since their own
sign-up, not a calendar month. The triangle is empty below the diagonal because..."
