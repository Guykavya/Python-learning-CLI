## Model answer

**1. Sensor, one missing hour.** A short outage in a process that changes smoothly (likely MCAR). I **interpolate** the
hour from its neighbours (or `ffill(limit=...)`), but only a **short** gap; a gap of days stays missing, because a long
repeated value would hide a broken sensor. In the report: how many hours were interpolated and the limit.

**2. Income skipped by young people.** Missingness depends on a visible column (age): **MAR**. Dropping those rows
makes the average too high (young people earn less). I **fill using the column that explains it** (the age-group
median or a random draw within the group), add a **missing indicator**, and report **both** answers (rows dropped, and
rows filled by age group) and the gap between them, because the mechanism is a judgement, not a measurement.

**3. A product with no sales rows in an open week.** Probably **zero in disguise**: no row means nothing was sold. I
check the logic (the shop was open and the product was on the shelf), and then I fill with **0**. Zero only when zero is
true: if the product was out of stock, the demand is unknown and 0 would understate it. In the report: "missing weeks
counted as zero sales".

**4. Test score of an absent student.** The score is **not applicable or not yet known**, and "absent" is information.
I do **not** fill it with the mean or with 0 (0 would claim the student failed). I keep it missing (or give it its own
category "absent") and compute statistics on the students who sat the exam, stating how many were absent. If the score
is the **target** of a model, I never fill it: those rows are dropped from training.

**Headline number.** If the choice could change it, I show the **same number under a second method** and say why they
differ, so the reader can judge.

**Checklist: your answer should mention**
- [ ] the mechanism or reason (MCAR, MAR, structural, zero in disguise)
- [ ] what the gap means (outage, skipped question, nothing sold, not applicable)
- [ ] report both answers (two methods, the gap)
- [ ] never fill a target (drop those rows from training)
- [ ] zero only when zero is true
- [ ] short gaps only for interpolation
