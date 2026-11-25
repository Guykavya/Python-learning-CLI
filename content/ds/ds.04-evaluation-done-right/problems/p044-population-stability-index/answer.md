## Model answer

1. - `monthly_charge` **0.05**: stable, within normal month-to-month variation. No action; keep monitoring.
   - `support_calls` **0.15**: a moderate shift. Investigate: is there a real change (a service outage producing more calls), a change in how calls are counted, or seasonality? Check whether the model's performance on recent labelled data has changed.
   - **score 0.4**: a major shift in the model's output. Act now: find which inputs moved, check for data problems, and check the effect on decisions (how many customers now cross the call threshold).
2. The score is what drives decisions. A big shift there changes **who gets called** today, even if each input moved only a little (small shifts in several inputs add up). It also means the model sees a population unlike its training data, so its probabilities may no longer be calibrated.
3. Causes that are not customer behaviour: a **unit or format change** (rupees to paise, as in the chapter: PSI 8.3), a **pipeline bug** (a column filled with zeros or missing values, a join that duplicates rows), a schema change upstream, or a new category that the feature code maps to a default.
4. PSI says the inputs changed, not that the model got worse; some shifts do not hurt accuracy. Before retraining, check **performance on recent labelled data** (AUC, calibration, cost) once labels arrive, look at **which features drifted** and **why**, and fix data bugs first. Retrain on data that represents the new situation, with the same honest evaluation.

**Checklist: your answer should mention**
- [ ] 0.05 stable / 0.15 moderate, investigate / 0.4 major, act
- [ ] the score distribution drives decisions and calibration, so its drift is urgent
- [ ] data bugs or unit changes can cause high PSI
- [ ] PSI is an alarm, not proof of worse performance
- [ ] check recent labelled performance before retraining
