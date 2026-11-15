**1. Chain length.** With keys spread evenly, each of the `m` buckets holds about `n / m = alpha` keys. A lookup computes the hash
(1 step) and then walks a chain of average length `alpha`, so it costs about `1 + alpha` steps. If `alpha` stays below a constant such
as 0.75 (because the table is resized), a lookup is O(1) on average.

**2. Why resize.** With `10^6` keys in 16 buckets, each chain has about `10^6 / 16 = 62500` keys. A lookup scans a chain of that size,
so the table is as slow as a list, O(n). Resizing keeps `alpha` bounded.

**3. Why double.** Start at size 1 and insert 16 keys, doubling when full: the resizes copy 1, 2, 4, 8 keys (and the next one
would copy 16), a total of 15, less than 2 per insert. In general the copies add up to less than `2n`, so each insert pays O(1) on
average: **amortised O(1)**. Growing by one bucket would copy 1, 2, 3, ..., n keys, a total of `n(n+1)/2`, O(n^2) overall.

**4. Open addressing.** Every key sits in a slot of one array, so when the table fills up the probe runs (clusters) get long
quickly. At load factor 1 there is no empty slot left, so a search for a missing key never meets the empty slot that tells
it to stop. Open addressing therefore resizes earlier (around 0.5 to 0.7), while chaining can work at 0.75 or even above 1.

**5. Deletion.** A chaining table just removes the key from its chain. In open addressing a key may sit in the middle of a probe
run for other keys. If the slot became empty, a search for a later key in the run would stop at the hole and report "missing".
So the slot is marked with a **tombstone** (searches continue through it, inserts may reuse it), or the later keys are shifted back.
