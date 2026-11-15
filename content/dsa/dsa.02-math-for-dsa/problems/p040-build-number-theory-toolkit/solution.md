## Approach

Split the work in two layers. The **parser** turns a line into `name` and a list of ints, or decides `error`. The **tools** are
ten small functions that do not know about input. This is how you keep a 100-line program correct: you can test each
function alone.

Parser order: empty line or unknown name, then argument count, then "every argument is digits", then (inside the
dispatcher) the range checks like `m >= 1`.

## Code

```python
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def lcm(a, b):
    g = gcd(a, b)
    if g == 0:
        return 0
    return a // g * b


def power_mod(a, b, m):
    result = 1 % m
    a = a % m
    while b > 0:
        if b & 1:
            result = result * a % m
        a = a * a % m
        b >>= 1
    return result


def ext(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1


def inverse(a, m):
    g, x, y = ext(a % m, m)
    if g != 1:
        return None
    return x % m


def ncr(n, r, m):
    if r > n:
        return 0
    r = min(r, n - r)
    c = 1
    for i in range(r):
        c = c * (n - i) // (i + 1)
    return c % m


def factorise(n):
    parts = []
    p = 2
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            parts.append((p, e))
        p += 1
    if n > 1:
        parts.append((n, 1))
    return parts


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def phi(n):
    result = n
    for p, e in factorise(n):
        result = result // p * (p - 1)
    return result


def popcount(n):
    count = 0
    while n > 0:
        n &= n - 1
        count += 1
    return count


def sieve(n):
    if n < 2:
        return []
    flags = [True] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if flags[i]:
            primes.append(i)
            for m in range(i * i, n + 1, i):
                flags[m] = False
    return primes


ARGS = {"gcd": 2, "lcm": 2, "inv": 2, "ncr": 3, "factor": 1, "isprime": 1,
        "phi": 1, "pow": 3, "popcount": 1, "sieve": 1}


def execute(name, v):
    if name == "gcd":
        return str(gcd(v[0], v[1]))
    if name == "lcm":
        return str(lcm(v[0], v[1]))
    if name == "inv":
        if v[1] < 1:
            return "error"
        x = inverse(v[0], v[1])
        return "none" if x is None else str(x)
    if name == "ncr":
        if v[2] < 1:
            return "error"
        return str(ncr(v[0], v[1], v[2]))
    if name == "factor":
        if v[0] < 1:
            return "error"
        parts = factorise(v[0])
        if not parts:
            return "1"
        return " ".join(str(p) + "^" + str(e) for p, e in parts)
    if name == "isprime":
        return "yes" if is_prime(v[0]) else "no"
    if name == "phi":
        if v[0] < 1:
            return "error"
        return str(phi(v[0]))
    if name == "pow":
        if v[2] < 1:
            return "error"
        return str(power_mod(v[0], v[1], v[2]))
    if name == "popcount":
        return str(popcount(v[0]))
    primes = sieve(v[0])
    if not primes:
        return "none"
    return " ".join(map(str, primes))


k = int(input())
for _ in range(k):
    parts = input().split()
    if len(parts) == 0 or parts[0] not in ARGS:
        print("error")
    elif len(parts) - 1 != ARGS[parts[0]]:
        print("error")
    elif not all(w.isdigit() for w in parts[1:]):
        print("error")
    else:
        print(execute(parts[0], [int(w) for w in parts[1:]]))
```

## Complexity

- `gcd`, `lcm`, `inv`: O(log) steps. `pow`: O(log b) multiplications.
- `isprime`, `factor`, `phi`: O(sqrt n), about 10^6 steps for `n = 10^12`.
- `ncr`: O(min(r, n - r)) big-integer steps (exact numbers up to a few thousand digits).
- `sieve`: O(n log log n) time and O(n) memory. `popcount`: O(number of 1 bits).

## Another way

For `ncr` with a **prime** modulus, factorial tables and Fermat inverses are faster per query (see the factorials problem).
For many `isprime` queries on big numbers a sieve of small primes or Miller-Rabin is much faster. For `ncr` with a composite
modulus and big `n`, you would need prime-power moduli and the Chinese remainder theorem (a good exercise after this module).

## Testing your own toolkit

Write small checks first: `gcd 0 0`, `inv 4 10`, `pow 5 0 1`, `factor 1`, `sieve 1`. Then compare against Python's built-ins:
`math.gcd`, `pow(a, -1, m)`, `pow(a, b, m)`, `math.comb`. Real contests are won by testing edge cases before submitting.
