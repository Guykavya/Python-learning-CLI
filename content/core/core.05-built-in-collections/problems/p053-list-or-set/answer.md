**List membership.** `name in seen` on a list compares `name` with `seen[0]`, then `seen[1]`,
and so on, until it finds an equal item or reaches the end. In the worst case (the name is not
there) it compares with every item. That is O(n).

**Why the loop is O(n²).** The check runs once per name, and the list keeps growing. If all
names are different, check number i compares against i earlier names. The total is
0 + 1 + 2 + ... + (n - 1), which is about n²/2. For n = 200,000 that is about 20,000,000,000
comparisons. Even at tens of millions of comparisons per second, that is minutes.

**Set membership.** A set is a hash table. `name in seen` computes `hash(name)`, jumps to the
slot it points to, and compares with whatever is there (usually zero or one item). The time
does not depend on how many names are stored: O(1) on average. The whole loop becomes O(n),
about 200,000 quick steps.

**What the set gives up.**

- **Order:** a set does not remember the order names were added, and it cannot be indexed.
- **Duplicates:** a set keeps one copy of each value. (Here that is exactly what we want.)
- **Hashable items only:** names are strings, which is fine, but a list could not be stored.
- **Memory:** the hash table keeps empty slots so it stays fast, so it uses several times more
  memory than a list of the same items.

**When a list is better.** When you need the items in order, by position, or with duplicates,
such as a queue of customers or the moves of a game. Also for very small collections, where a
quick scan costs less than hashing. If you need both order and fast membership, keep both: a
list for order and a set for "seen" (or a dict, which keeps insertion order).

Key ideas to check: list `in` is a linear scan, O(n); a loop of them is O(n²) with an estimate;
set uses hashing, O(1) average; trade-offs in order, duplicates, hashability and memory.
