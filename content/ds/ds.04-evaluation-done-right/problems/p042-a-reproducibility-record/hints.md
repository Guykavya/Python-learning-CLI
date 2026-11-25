## Hint 1

For the fingerprint, which two things go into the hash, in which order? For the record, which function turns a dataclass into a plain dict?

## Hint 2

```text
h = sha256(); h.update(",".join(map(str, df.columns)).encode()); h.update(hash_pandas_object(df, index=False).to_numpy().tobytes())
return h.hexdigest()[:16]
run_experiment: split -> fit -> p = predict_proba(test)[:, 1] -> build the dict with asdict(cfg), roc_auc_score, brier_score_loss
```
