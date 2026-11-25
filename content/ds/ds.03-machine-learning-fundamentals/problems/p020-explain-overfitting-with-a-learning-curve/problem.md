# Explain overfitting with a learning curve

The module's main outcome: *explain overfitting with a learning curve.* Below is a real learning curve from the chapter. A **degree-12 polynomial** was fitted to noisy sine data (noise sd 0.3, so the best possible RMSE is about 0.30). Each row averages 30 random training sets of that size; the validation set is fixed.

```text
 n_train  train_rmse  val_rmse       gap
      12      0.1450   78.9080   78.7630
      20      0.1910    7.4090    7.2180
      40      0.2550    0.4290    0.1730
      80      0.2720    0.3300    0.0590
     160      0.2800    0.3140    0.0340
     320      0.2890    0.3080    0.0190
```

(For comparison, the chapter's degree-1 line gave about 0.51 train and 0.53 validation at 320 rows.)

Write your answer in `answer.md`, in clear sentences, covering:

1. What does this table show about the model **at 12 rows**? Name the problem and say what the two errors tell you.
2. What happens to the training error, the validation error and the gap as `n_train` grows? Why does the training error **rise**?
3. At about which size does the model stop being a problem, and what does the final row (320) say about it?
4. What would you try next if you could not collect more data? Name two options.
5. Why does this curve look different from a curve for an underfitting model (the straight line)?

## After you answer

Compare with the model answer and tick the checklist for the points you made.
