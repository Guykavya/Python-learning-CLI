# A reproducibility record

Chapter sections 13.5-13.6. An experiment is reproducible when you can say exactly **what you chose** (configuration), **what you fed it** (a fingerprint of the data) and **what came out** (metrics), and running it again gives the same numbers.

The configuration is a dataclass (the tests pass one in):

```python
@dataclasses.dataclass
class Config:
    name: str = "churn-logreg"
    seed: int = 0
    test_size: float = 0.25
    C: float = 1.0
    features: tuple = ("tenure_months", "monthly_charge", "support_calls", "autopay")
```

Write two functions:

- `data_fingerprint(df)`: a SHA-256 hash of the column names (joined with `,` and UTF-8 encoded) followed by the bytes of `pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes()`; return the first **16** hex characters. (This is the chapter's function.)
- `run_experiment(cfg, df)`: split `df[list(cfg.features)]` and `df["churned"]` with `train_test_split(test_size=cfg.test_size, random_state=cfg.seed, stratify=y)`; fit `make_pipeline(StandardScaler(), LogisticRegression(C=cfg.C, max_iter=2000, random_state=cfg.seed))`; return the record

```text
{"config": dataclasses.asdict(cfg),
 "data": {"fingerprint": data_fingerprint(df), "rows": len(df)},
 "metrics": {"test_auc": round(AUC, 6), "test_brier": round(Brier score, 6)}}
```

## Example

```text
run_experiment(Config(), df) == run_experiment(Config(), df)     -> True
change one cell of df                                            -> a different fingerprint
```
