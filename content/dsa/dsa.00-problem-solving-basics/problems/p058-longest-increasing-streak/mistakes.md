- Comparing with the best only when a streak breaks. A streak that runs to the last number is never
  compared, so `5 1 2 3 2 4 6 7` reports length 3 instead of 4.
- Using `>=` when updating the best. On ties the **later** streak replaces the earlier one, but the
  earliest must be reported.
- Using `x >= prev` to continue a streak. Equal values are not strictly increasing, so `3 3 3` would
  wrongly be one streak of length 3.
- Forgetting to set the new start position when a streak breaks. The length is right but `from S to E`
  points at the wrong place.
