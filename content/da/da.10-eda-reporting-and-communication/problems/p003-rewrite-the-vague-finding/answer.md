## Model answer

**Headline.** Weekly active users fell from 182,000 to 161,000 after the 3 March app update, mainly because crashes on Android 12 rose from 0.4% to 3.1% of sessions.

**Recommendation.** Ship the Android 12 crash fix (owner: Head of Mobile; by 31 March), and add a crash-rate guardrail to the release checklist (owner: QA lead; by 15 April).

**Impact.** About 21,000 weekly active users are missing. If the crash explains most of the drop, the fix should bring back roughly 12,000 to 18,000 of them within a month; we will know within two weeks of the release.

**Evidence.** Users who saw a crash were 2.4 times as likely to be inactive the next week (95% CI 2.1 to 2.8).

**Limitation.** The data are observational: the update also changed the home screen, which could explain part of the drop.

**What was wrong with the original.** It had no number, no comparison and no cause, so the reader could not judge the size of the problem. "Monitor the situation" and "further analysis" name no action, owner or date, so nobody would do anything.

**Checklist: your answer should mention**
- [ ] a headline with a number and a comparison (from 182,000 to 161,000)
- [ ] the cause in the headline
- [ ] an action with an owner and a date
- [ ] the impact as a range in users
- [ ] the uncertainty (interval or a limitation)
- [ ] a limitation (observational data, other changes in the update)
