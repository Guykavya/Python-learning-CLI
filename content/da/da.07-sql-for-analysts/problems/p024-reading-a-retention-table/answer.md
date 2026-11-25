## Model answer

Each **row** is a **cohort**: the users who signed up in the same month (Jan has 100 users). Each **column** is the number of
months *since that cohort's own sign-up* (M0 is the sign-up month), not a calendar month: M1 is February for the January
cohort and March for the February cohort. A cell is the share of the cohort's users that were active in that month.
The bottom-right corner is empty because those months **have not happened yet** at the time of the extraction: the April
cohort has only M0. These are immature cells: they should be empty (`NULL`), never 0.

About newer against older users, compare **within a column**, where every cohort has been observed for the same time: M1 is
60, 55, 62 for Jan, Feb, Mar, so there is no clear trend (a few points up or down with small cohorts could be noise). We cannot say anything
about April's month 3, or about how March will look at M2; the table only shows what has been observed.

A **pooled curve** gives one retention value per month number: for each column, add the active users of every cohort
that has that cell and divide by the sum of **those cohorts'** sizes. That weights big cohorts more, and uses only cells that
exist (M3 comes from January alone, so it is the least certain point). Cells that do not exist are not zeros and not
averaged in.

Raw counts of active users mislead because cohorts differ in size (100, 120, 90, 150): 60 active users in a cohort of 100 and
72 in a cohort of 150 are 60% and 48%.

**Checklist: your answer should mention**
- [ ] cohort = signup month (row)
- [ ] month number since signup, not calendar month (column)
- [ ] immature cells: empty because not yet observed, not zero
- [ ] pooled curve weights by cohort size and uses only existing cells
- [ ] do not compare raw counts; compare percentages in the same column
