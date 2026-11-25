## Model answer

**The counts.** Take 100,000 people. With a prior of 1 in 1,000, **100** are sick and **99,900** are healthy. With 99% sensitivity the test finds `99` of the sick (true positives). With a 1% false positive rate it also flags `999` of the healthy (false positives). Among about `1,098` positive tests only `99` are really sick: the probability of being sick after a positive test is `99 / 1098`, about **9%**, not 99%.

**Base rate.** "99% accurate" describes `P(positive | sick)`, but the patient wants `P(sick | positive)`. These two are different, and the link between them is the **base rate**: when the disease is rare, the healthy group is so large that even a small false positive rate produces many more false alarms than there are true cases. Ignoring the prior is the **base rate fallacy**.

**What would make a positive convincing.** A higher prior (test only people with symptoms or a high-risk group), a much lower false positive rate, or a **second independent test**, which uses the 9% as the new prior (see the sequential update): two positives raise the probability a lot.

**Checklist: your answer should mention**
- [ ] a count of true positives and false positives out of 100,000 people (99 against about 999)
- [ ] `P(positive | sick)` is not `P(sick | positive)`
- [ ] the base rate (prior) is small, so false positives outnumber true positives
- [ ] a second test or a higher prior fixes it
