## Model answer

**1. Definitions.** The question is always: what does the chance that `income` is missing depend on?
- **MCAR** (missing completely at random): on **nothing**; it is a coin flip.
- **MAR** (missing at random): on **other columns that I can see** (age, city, education), not on the missing value itself.
- **MNAR** (missing not at random): on the **missing value itself** (the hidden income).

**2. Survey examples.**
- MCAR: a page of the paper form was lost in the post, or the export dropped random rows.
- MAR: young respondents (or people with little schooling) skip the income question more often. Age or education is
  in the table, so the pattern can be seen.
- MNAR: high earners do not want to tell their income. The reason sits in the value we do not have.

**3. Effect on the complete-case mean of `income`.**
- MCAR: **no bias**, only fewer rows (a wider margin of error). The chapter's observed mean was 34,356 against a truth
  of 34,341.
- MAR: **biased**, because the survivors are not like the population (if the low-education group skips more, the
  mean is too high: 36,271). It can be **repaired** by using the visible columns that explain the missingness
  (fill within groups, regression, random draw within groups).
- MNAR: **biased** (if high earners hide, the mean is too low: 30,070), and **not repairable** from the data: the
  missing values are exactly the ones the data do not show. The honest answer is a **range** (sensitivity analysis).
  MAR and MNAR can bias in opposite directions: there is no rule such as "missing data lowers the average".

**4. From the data alone?** I can **look for MAR**: compare the missing rate across groups of other columns, or compare
other columns between missing and present rows (a slope or a gap is a sign). I **cannot prove MCAR**, and I cannot tell
MAR from MNAR, because the difference is whether the cause is a visible column or the hidden value. That is a
question for the people who ran the survey: who skips this question, and why?

**Checklist: your answer should mention**
- [ ] missing completely at random (a coin flip, no pattern)
- [ ] depends on an observed column (MAR)
- [ ] depends on the missing value itself (MNAR)
- [ ] bias of the complete-case mean (none, repairable, not repairable)
- [ ] cannot be proven from the data alone (MAR vs MNAR needs knowledge of how the data was collected)
- [ ] the direction of the bias depends on who is missing
