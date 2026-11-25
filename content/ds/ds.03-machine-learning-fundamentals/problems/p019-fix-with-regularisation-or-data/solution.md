## Walk-through

`1.25 * 0.30 = 0.375`.

- S1: gap 0.85 > 0.15 * 0.90 = 0.135, and `still_falling` is True: `collect more data`.
- S2: gap 0.50 > 0.15 * 0.60 = 0.09, `still_falling` False: `regularise or simplify`.
- S3: gap 0.03 vs 0.15 * 0.55 = 0.0825: small gap; val_err 0.55 > 0.375: `add capacity or features`.
- S4: gap 0.02 vs 0.15 * 0.31 = 0.0465: small gap; val_err 0.31 not > 0.375: `stop: near the noise floor`.

## Why S1 and S2 differ

Both overfit. If the gap is still shrinking as rows are added (S1), more data will close it. If it is flat (S2), more rows would not help and you must reduce the model's freedom (a simpler model, regularisation, fewer features). `still_falling` comes from comparing the gap at the last size with the gap a few sizes earlier.
