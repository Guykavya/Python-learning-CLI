# Study roadmap and routine

How to move through the course without burning out. Nothing is locked: use `learn goto` to jump.

## Pick a path

| Goal | Tracks, in order | Rough time at 90 min/day |
|---|---|---|
| Strong Python base | core (24 modules) | 5–6 months |
| Backend jobs | core → shared → swe → dsa (parallel, light) | 9–12 months |
| Data analyst | core 1–17 → shared → da | 6–8 months |
| Data scientist / ML | core 1–17 → da → ds → ml | 10–14 months |
| LLM engineer | core → swe 1–6 → ml 1–3 → llm | 10–12 months |
| Interviews / contests | dsa, alongside any path above | ongoing |

Set the focus so the daily plan follows your path: `learn focus core swe dsa`.

## One day (90 minutes)

1. **10 min, warm-up**: `learn review`. Re-solve what is due. Do this first, while fresh.
2. **30 min, read**: `learn read <module>`. One or two `##` sections only. Press `a` for answers after you predicted.
3. **45 min, solve**: `learn start <problem>`. Attempt for 15 minutes before the first `learn hint`.
4. **5 min, close**: write one line about what confused you. Next day it is your first question.

## One week

- 5 study days, 1 review-only day, 1 rest day.
- End the week with `learn stats topics`; the weakest topic becomes Monday's focus.
- Once a month run `learn cards core.NN` and review the cards in Anki or on paper.

## Rules that work

- **Attempt before hints.** A struggle of 15 minutes teaches more than reading a solution.
- **Type the code.** Do not paste chapter examples; change a value and predict the result first.
- **Never skip the trace/explain problems.** They train reading code, the skill interviews test.
- **Do the module project.** Each module ends with a small project; it is what you will remember.
- **Finish the capstone of a track** (`learn capstone <track>`) before starting the next track.
- When stuck for more than 30 minutes: `learn stuck`, sleep, retry. Do not read the full solution on the first try.

## When you fall behind

Do not catch up. Run `learn resume`: it gives a warm-up after a long break. Lower `plan.daily_minutes`
(`learn config set plan.daily_minutes 45`) rather than stopping.
