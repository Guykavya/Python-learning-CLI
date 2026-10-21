## Walkthrough

**Loop A** (`<`, increment after print):

| i at check | `i < 3` | printed | i after body |
|---|---|---|---|
| 1 | True | `A 1` | 2 |
| 2 | True | `A 2` | 3 |
| 3 | False | (loop ends) | 3 |

Then `A ends at 3`.

**Loop B** (`<=`, increment before print):

| i at check | `i <= 3` | i after `i += 1` | printed |
|---|---|---|---|
| 1 | True | 2 | `B 2` |
| 2 | True | 3 | `B 3` |
| 3 | True | 4 | `B 4` |
| 4 | False | (loop ends) | |

Then `B ends at 4`.

**Loop C** (`<`, increment before print):

| i at check | `i < 3` | i after `i += 1` | printed |
|---|---|---|---|
| 1 | True | 2 | `C 2` |
| 2 | True | 3 | `C 3` |
| 3 | False | (loop ends) | |

Then `C ends at 3`.

## Key idea

Two separate choices control a counting loop: the comparison decides **how many** times the body
runs (`< 3` from 1 runs twice, `<= 3` runs three times), and the position of the increment decides
**which values** you see (before the print shifts every printed value up by one). After the loop,
the counter always holds the first value that made the condition false, which is usually one step
past the last value used. When a loop is off by one, check these two choices separately, and trace
the first and last iteration by hand.
