**1. Definition.** A sort is stable if records with equal keys stay in the same relative order as in the input. Here `ann` and `cy` both have key 30, and `ann` comes first in the input; `bob` and `dee` both have 25, `bob` first.

**2. The output.** Stable: `[('bob', 25), ('dee', 25), ('ann', 30), ('cy', 30)]`. An unstable sort may also return `[('dee', 25), ('bob', 25), ...]` or put `cy` before `ann`. Both are correctly sorted by age, but only the stable result keeps the ties in input order.

**3. Why it matters.** A spreadsheet sorted by city and then by last name: sort by name first, then by city; people in the same city should remain in name order. Another case: a leaderboard that lists players with equal points in the order they scored.

**4. Recipe.** Sort by the *less important* key first (`name`), then by the more important key (`age`). The second, stable sort only reorders when ages differ, so ties on age keep the name order from pass one. The last sort has the highest priority.

**5. Stable or not.** Stable: merge sort, insertion sort, bubble sort, Python's `sorted`/`list.sort` (Timsort), counting sort when filled from the back. Not stable: selection sort (swaps jump over equal items), heap sort, and the common in-place quicksort.
