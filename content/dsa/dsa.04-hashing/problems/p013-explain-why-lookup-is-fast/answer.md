**1. List cost.** A failed `x in items` compares `x` with every one of the `n = 100000` items before answering "no".
For 100000 values that is about `100000 * 100000 = 10^10` comparisons, minutes of Python.

**2. Set cost.** The set computes `hash(x)`, a number, and uses it to jump straight to one bucket (slot) in its table.
It only compares `x` with the (usually zero or one) items stored in that bucket. It never walks the whole collection.
That is why 100000 checks take a fraction of a second.

**3. Average vs worst.** If many different values land in the same bucket (collisions), the lookup has to compare
with all of them, up to O(n). With a good hash function and a table that grows when it gets full, buckets stay
short, so the average cost per lookup is O(1). Bad or deliberately chosen inputs can break this.

**4. The price.** A set keeps spare empty slots (more memory than a list), it has no positions or order you can rely on,
and building it costs more than appending to a list.

**5. Requirement.** Items must be hashable: immutable, with a hash that never changes while stored, and equal values must
have equal hashes. Otherwise the set would look in the wrong bucket and fail to find an item it holds.
