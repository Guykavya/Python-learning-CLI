## Walk-through

**logistic vs rule**: differences 0.06, 0.05, 0.06, 0.05, 0.06. Mean 0.28 / 5 = 0.056. Deviations 0.004, -0.006, 0.004, -0.006, 0.004; squares sum to 0.000120; divided by 4 is 0.000030; sd = 0.005477; se = 0.005477 / 2.2361 = 0.0024. Two se = 0.0049 < 0.056: `better`.

**boosting vs logistic**: differences 0.01, -0.01, 0.01, -0.01, -0.01. Mean -0.01 / 5 = -0.002. Deviations 0.012, -0.008, 0.012, -0.008, -0.008; squares sum to 0.000480; / 4 = 0.000120; sd = 0.010954; se = 0.0049. The mean (-0.002) is not above 2 se: `no clear difference`.

## The best fold

A single fold is one draw. Boosting wins two folds and loses three; the paired differences average to about zero. "Better" is a statement about the average difference relative to its noise.
