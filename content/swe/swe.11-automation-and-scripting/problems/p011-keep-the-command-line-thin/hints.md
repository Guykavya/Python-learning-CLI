## Hint 1

Pick one behaviour (the dry run) and write, in your head, the test for it in both designs: what do you need to set up, and what do you compare? Then imagine three callers of "organize": argparse, Click, and `run_job` at 3 a.m. Which of them can call a Click command comfortably?

## Hint 2

Structure each part as **situation, consequence, rule**: "With both front ends, a bug in the move logic must be fixed in two places (situation); one will be forgotten (consequence); so the logic lives in one library both call (rule)." For part 4, copy the shape of the chapter's "Try it: spot the thin layer" answer.
