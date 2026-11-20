## Hint 1

Draw the three moments on a line: receive -> effect -> ack. Mark where the ack is in each guarantee. Now place a crash before and after the effect, and ask: "after the restart, does the broker still have the job?"

## Hint 2

For part 2, ask: could the worker send the e-mail and record the ack in one transaction? Who would run that transaction, the e-mail provider or the broker? For part 4, ask for each job: "which is worse, losing it or doing it twice?" and "is it already harmless to repeat?"
