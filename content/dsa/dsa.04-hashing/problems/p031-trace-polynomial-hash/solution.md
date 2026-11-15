## Walkthrough

| word | steps | final hash |
|---|---|---|
| abc | 1, 33, 16 | 16 |
| cab | 3, 3*31+1 = 94, 94*31+2 = 2916 % 101 = 88 | 88 |
| abd | 1, 33, 33*31+4 = 1027 % 101 = 17 | 17 |
| zz | 26, 26*31+26 = 832 % 101 = 24 | 24 |
| ga | 7, 7*31+1 = 218 % 101 = 16 | 16 |

## Output

```
abc
  after a h = 1
  after b h = 33
  after c h = 16
hash 16
cab
  after c h = 3
  after a h = 94
  after b h = 88
hash 88
abd
  after a h = 1
  after b h = 33
  after d h = 17
hash 17
zz
  after z h = 26
  after z h = 24
hash 24
ga
  after g h = 7
  after a h = 16
hash 16
```

## Key ideas

- Order matters: each earlier letter is multiplied by `B` once more for every letter after it.
- Only 101 hash values exist, so some words must share a hash: **collisions** are unavoidable. Here `abc` and `ga` collide.
- Equal hash does not mean equal strings. A match must be **verified** (compare the strings) unless a wrong answer is acceptable.
- Real programs use a large `M` (about 10^9 or more) to make collisions rare.
