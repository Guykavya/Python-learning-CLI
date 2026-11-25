## Model answer

**Data leakage** means the evaluation lets the model use information it will not have when it makes real predictions, so the score answers an easier question than the one the business asks.

Here, `retention_offer_sent` is written **when a customer calls to cancel**, that is, after the churn decision. In the history, "got an offer" almost always means "churned", so cross-validation rewarded the model for reading the answer: 0.968. At the moment we must predict, no offer has been sent yet, so the column does not exist. The real skill is about 0.76.

On future customers the column is 0 for everyone. AUC only looks at order, and a constant column cannot change an order, so the leaky model ranks like the honest one (0.778 vs 0.770). But its probabilities are wrong: it learned "no offer = safe", so it predicts a mean churn of 0.024 against a true 0.235, and at a 0.5 threshold it finds nobody (recall 0). Anyone acting on its probabilities would call no one.

**Golden rule**: build the evaluation from what is known at prediction time, and fit anything that learns (scalers, selectors, encoders, models) on training rows only. Ask of every column: *who writes it, and when, relative to the moment we predict?*

Next, check the other families: preprocessing fitted on all rows, duplicates or the same customer on both sides of the split, and time order (train on the past, test on the future).

**Checklist: your answer should mention**
- [ ] leakage = information not available at prediction time used in training or evaluation
- [ ] the offer column is written after the outcome (timeline)
- [ ] the 0.968 measured an easier question; the honest skill is about 0.76
- [ ] on the future the AUC falls back, and the probabilities collapse (mean 0.024, recall 0)
- [ ] the golden rule: learn only from training rows, only from information known at prediction time
- [ ] the question "who writes this column and when?"
- [ ] at least one other leakage family named
