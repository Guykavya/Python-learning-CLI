## Walk-through

1. credit card fraud: not ranking; rate 0.01 < 0.05; `cost_fn` 100 > `cost_fp` 1: `recall`.
2. spam filter: rate 0.30 not rare; costs differ; `cost_fp` 50 > `cost_fn` 1: `precision`.
3. interview shortlist: `ranking_only` is True: `AUC`.
4. quality check: not ranking, rate 0.5 not rare; `cost_fp == cost_fn`: `accuracy`.
5. rare disease screening: rate 0.02 < 0.05; `cost_fn` 50 > `cost_fp` 5: `recall`.
6. production line stop alarm: rate 0.01 < 0.05; `cost_fn` 20 > `cost_fp` 500? No: `precision`.

## Why precision for the alarm

When a false alarm is 25 times more costly than a miss, you want few false alarms: the metric that punishes false positives is precision (flagged cases that are real).
