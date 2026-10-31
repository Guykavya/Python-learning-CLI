## Hint 1

Try it: print `hash(Version('1.0'))` and `hash(Version('1.00'))`. Are they equal? Now think about which shelf (bucket) a lookup visits.

## Hint 2

```
1. a == b  =>  hash(a) == hash(b)        (one direction only)
2. lookup: hash -> bucket -> == on entries in that bucket
3. Mia hashes text, == compares numbers -> equal objects, different hash -> wrong bucket
4. hash(self.parts) ; hash what you compare
5. unhashable beats a silently wrong dict
```
