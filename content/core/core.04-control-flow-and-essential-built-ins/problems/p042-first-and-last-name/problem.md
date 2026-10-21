# First and last name ignoring case

Read a line of names. Print:

```
First: <name that comes first alphabetically>
Last: <name that comes last alphabetically>
Longest: <longest name>
```

Compare **ignoring capital letters**, but print each name exactly as it was typed. When two
names are equal ignoring case (like `amit` and `Amit`), or tie on length, report the one
that appears first in the line.

If there are no names, print `No names`.

**Example**

Input `zoya Aarav meera Bhavesh`. Output:

```
First: Aarav
Last: zoya
Longest: Bhavesh
```

(Plain `min` would give `Aarav` here too, but `max` would wrongly give `meera`'s neighbour...
try it: capitals sort before all small letters.)
