## Model answer

If the banner does nothing at all and we test eight segments at the 5% level, the chance that **at least one** looks significant is `1 - 0.95^8`, about 34%. So a p-value of 0.03 in one of eight slices is exactly what luck produces about a third
of the time: it is **not a result**.

A segment also has only a fraction of the visitors, so its estimate is noisy and its interval wide; among slices that happen to look significant, the lift is typically **exaggerated** (the same selection effect as in an underpowered test).
And the segment was chosen **after** seeing the data: nobody planned "mobile in Large cities" in advance.

The team should treat it as a **hypothesis**. Either decide the segments before the next test (pre-registration) and power the test for them, or run a new experiment aimed at that segment with its own sample size and a control group.
If the segments must be looked at now, test the interaction once and correct for the number of comparisons. Until then, no rollout on this evidence.

**Checklist: your answer should mention**
- [ ] multiple comparisons: about a one-in-three chance of at least one false hit with 8 segments
- [ ] a small segment means a wide interval and an exaggerated estimate
- [ ] the segment was picked after seeing the data
- [ ] pre-register segments or run a follow-up test for the segment
- [ ] correct for the number of looks if you must decide inside the test
