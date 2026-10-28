## Hint 1

Draw three boxes: one for the class `Player` (team, lives, badges), one for `p`, one for `q`.
At the start, `p` and `q` hold only `name`. For every line ask: is this a **read** (look in the
object box, then the class box) or an **assignment** (always write in the object box)?

## Hint 2

Walk the tricky lines:

```
p.team = "blue"      -> p's box gets team = "blue"; the class keeps "red"
Player.team = "green" -> the class box changes; q has no own team, so q sees it
p.lose_life()         -> read p.lives (class: 3), write p.lives = 2 in p's box
q.earn("gold")        -> read q.badges (the ONE class list), append to it
p.badges = [...]      -> p's box gets its own list; the class list is untouched
del p.team            -> p's box loses team; reading p.team falls back to the class
```
