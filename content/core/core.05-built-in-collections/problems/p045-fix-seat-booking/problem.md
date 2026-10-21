# Fix the seat booking program

A classmate wrote a cinema seat booking program. It runs, but it gives wrong answers. **Fix**
`starter.py` (copy it into `solution.py` first) so that it follows this specification.

**Specification.** The first line is `rows cols`. Every seat starts free (`.`). Then read
commands until `done`:

| Command | What to do |
|---|---|
| `book R C` | if seat (R, C) is free, mark it `X` and print `Booked R C`; otherwise print `Seat R C is taken` |
| `undo` | cancel the **most recent** booking that has not been undone yet, print `Undid R C`; if there is none, print `Nothing to undo` |
| `save` | remember a snapshot of the seats as they are now, and print `Saved` |

Rows and columns count from 0. After `done`, print:

```
Seats:
<one line per row>
Free: <number of free seats>
Snapshot:
<one line per row of the last saved snapshot>
```

If `save` was never used, the snapshot is the layout at the start (all free). A snapshot must
not change when seats are booked or undone later.

**Example**

Input:
```
2 3
book 0 0
save
book 1 2
book 0 0
undo
book 0 1
done
```
Output:
```
Booked 0 0
Saved
Booked 1 2
Seat 0 0 is taken
Undid 1 2
Booked 0 1
Seats:
XX.
...
Free: 4
Snapshot:
X..
...
```

There are at least four bugs. The tests explain what each one causes.
