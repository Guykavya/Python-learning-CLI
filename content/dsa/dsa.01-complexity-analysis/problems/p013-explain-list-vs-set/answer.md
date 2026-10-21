**1. `in` on a list is a loop.** Python compares `word` with the first element, then the second, and so on, until
it finds a match or reaches the end. For a word that is not there, it must look at every element. So the time is
proportional to the list's length: the table shows it growing about 10 times each time the list grows 10 times
(5.6, 50, 556, 6283 microseconds). That is O(n) per lookup. If the word is present, on average it is found
halfway, which is still O(n).

**2. With a list the program is O(n * m).** It does `m` lookups, each up to `n` comparisons. Here that is up to
`100000 * 200000 = 2 * 10^10` comparisons. At roughly half a millisecond per lookup in a 100000-element list
(about a millisecond for 200000), 100000 lookups take on the order of 100 seconds or more.

**3. A set uses hashing.** When a value is added, Python computes a number from it (its hash) and uses that
number to choose a slot in a table. To check `word in s`, it computes the hash of `word` again and looks only in
that slot (and occasionally a few nearby slots if two values landed together). It never walks through the other
elements, so the time does not depend on how many there are: O(1) on average, which the constant 0.07 microseconds
in the table shows. Building the set costs O(n) once (one hash and insert per word). The program becomes
O(n + m): about 300000 cheap steps instead of 2 * 10^10.

**4. When a list is right.** A list keeps order and duplicates and allows positions: use it when you need "the
3rd item", sorting, or repeated items. For a handful of lookups on a small list, the list is fine and building a
set is not worth it. A set cannot hold unhashable things like lists, keeps no order, cannot be indexed (`s[0]` is
an error), and stores each value only once. Also, the O(1) is an average: a set's worst case is O(n) if many values
have colliding hashes, which practically never happens with normal data.

Key ideas to check: list `in` scans element by element, O(n), the table grows 10x with size; program is O(n * m),
about 2 * 10^10; set hashes the value and jumps to one slot, O(1) average, flat table row; building the set is O(n);
total O(n + m); lists keep order, duplicates and indexing; sets need hashable items.
