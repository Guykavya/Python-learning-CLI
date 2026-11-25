## Walk-through

Threshold 20 / 100 = 0.2.

- Model probabilities >= 0.2: C (0.30) and D (0.60). B's 0.15 is below.
- Observed rates >= 0.2: B (0.30), C (0.55), D (0.85). A's 0.10 is below.
- Bin B: skipping costs 0.30 * 100 = 30.0 per customer; calling costs 20.0.

## The cost of miscalibration

The model says 15% for bin B but 30% churn. It tells the team to skip bin B, which costs 30 per customer instead of 20: **10 extra per customer**, 1,000 per 100 such customers. The ranking can be perfect and the decisions still wrong if the probabilities are off.
