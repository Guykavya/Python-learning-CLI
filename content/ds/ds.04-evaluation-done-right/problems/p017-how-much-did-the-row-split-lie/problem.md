# How much did the row split lie?

Chapter section 6.2. In the chapter's patient simulation, each patient has stable personal "fingerprint" measurements and a hidden personal risk. With a **row** split the model meets the same patients in training and validation and scores well by recognising them. With a **group** split it must generalise to new patients.

Write `row_vs_group_cv(X, y, groups, model)` returning `(row_auc, group_auc)`:

- `row_auc`: mean `cross_val_score(model, X, y, cv=KFold(5, shuffle=True, random_state=0), scoring="roc_auc")`
- `group_auc`: mean `cross_val_score(model, X, y, cv=GroupKFold(5), groups=groups, scoring="roc_auc")`

<details><summary>The data generator <code>make_patients</code> (chapter section 6.2)</summary>

```python
def make_patients(n_patients=80, visits=15, seed=0):
    r = np.random.default_rng(seed)
    pid = np.repeat(np.arange(n_patients), visits)
    finger = r.normal(0, 1, (n_patients, 4))                 # stable personal traits
    risk = r.normal(0, 1.6, n_patients)                      # personal tendency (hidden)
    symptom = r.normal(0, 1, n_patients * visits)
    logit = risk[pid] + 0.6 * symptom
    y = (r.random(n_patients * visits) < 1 / (1 + np.exp(-logit))).astype(int)
    X = np.column_stack([finger[pid] + r.normal(0, 0.05, (n_patients * visits, 4)), symptom])
    cols = ["trait_a", "trait_b", "trait_c", "trait_d", "symptom_score"]
    return pd.DataFrame(X, columns=cols), y, pid
```
</details>

## Example

```text
Xp, yp, pid = make_patients()
row_vs_group_cv(Xp, yp, pid, KNeighborsClassifier(5))   ->  (0.75, 0.56)
```
The row split overstates the skill on new patients by about 0.2.
