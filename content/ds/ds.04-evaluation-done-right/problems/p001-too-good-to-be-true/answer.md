## Model answer

1. 0.99 is far above what the problem allows (experts reach about 0.75, and churn depends on things no table records). When a model beats a known ceiling by that much, the usual explanation is that the evaluation lets the answer into the features or the validation rows: **leakage**. Too good to be true is a signal to investigate, not to deploy.
2. Three checks:
   - **Single-feature scores**: score each column alone. A single column with AUC near 0.95 is suspect: ask how and **when** it is filled in.
   - **Shuffled-label check**: shuffle the target and rerun the whole pipeline. An honest pipeline scores about 0.5; anything clearly above 0.5 means the pipeline itself leaks (for example selection or scaling on all rows).
   - **Timeline / split check**: list for every column when its value becomes known compared with the prediction moment, and check the split matches deployment (later customers, new customers). A column known only after the outcome, or the same customers on both sides, confirms a problem.
3. At prediction time that column does not exist yet (it is empty or zero for everybody). The model's ranking falls back to the honest level at best, and its probabilities are badly wrong: it learned "no offer means safe", so it predicts almost nobody will churn.

**Checklist: your answer should mention**
- [ ] a score far above the known ceiling suggests leakage
- [ ] single-feature scores to find a column that contains the answer
- [ ] shuffled-label check: an honest pipeline scores about 0.5
- [ ] check the timeline: is every feature known at prediction time?
- [ ] in production the leaky column is missing, so the score and the probabilities collapse
