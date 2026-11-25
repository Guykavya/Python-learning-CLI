## Model answer

**1. The Rs 9,00,000 order.** It is far from the median, but "far" is not "wrong". The same customer has 40 orders,
so this is probably a real, very valuable customer (or a business account): a **real but extreme** value. I would
**keep** it, **flag** it with a Boolean column, and check the source: ask whoever owns the order system, or look at the
invoice. If it is a company, it belongs to a different population and I would report it in its own group. In the
report: "one order of Rs 9,00,000 (a repeat customer) was kept; the mean order value is X with it and Y without it;
the median is unchanged". Because it moves the mean a lot and the median little, I would report the median as the
typical order and show both.

**2. Age 140.** This is **impossible** by a domain rule (the questionnaire allows 18 to 75, and nobody is 140). It is
an entry error. I cannot prove what the true age was, so I do not guess a fix. I **set it to missing**, keep a
**flag** column (or a reason code) so the change is visible, and then treat it as a missing-data question. I check the
source form first if I can: maybe it is a typo for 40 or 14. In the report: "1 age above 120 set to missing".

**3. The stuck sensor.** A real room does not hold 24.3 degrees for eight hours while its neighbours change, so a
**stuck sensor** is likely: the value is a machine fault, not a measurement. I **flag** the run, **set those hours to
missing** with the reason "stuck" (a run rule, not a range rule: the value 24.3 is perfectly plausible on its own),
and check the source: ask facilities whether the sensor was serviced, compare with the neighbours. The gap is then a
missing-data question (interpolate only a short gap, keep a long one visible).

**Why not just delete.** A deleted row leaves no trace, changes the sample (the customer may be the most valuable
one), and cannot be undone. Flagging keeps the raw value, the reason and the decision, so a colleague can disagree
and rerun the analysis a different way. The effect of the decision (mean with and without) goes into the report.

**Checklist: your answer should mention**
- [ ] domain knowledge first (what is possible or normal in this world)
- [ ] a rule only flags suspects; a human decides (error or real value)
- [ ] flag, do not delete silently (keep a flag or reason column)
- [ ] check the source (the invoice, the form, the sensor log, the data owner)
- [ ] report the effect (statistic with and without the suspect, median vs mean)
- [ ] the three cases are different: real but extreme, impossible, stuck run
