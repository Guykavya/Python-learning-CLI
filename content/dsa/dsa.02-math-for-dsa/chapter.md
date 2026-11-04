# dsa.02 Math for DSA

## 1. Why math shows up in DSA

Open any list of contest or interview problems and a surprising number of them are, underneath, small pieces of
number theory: "is this number prime?", "what is the greatest common divisor of these values?", "how many ways can
I choose 5 items from 1,000, modulo 1,000,000,007?", "which single number appears an odd number of times?".

None of these needs advanced mathematics. They need about ten **tools**, each of them a few lines of code, and the
habit of recognising which tool a problem is asking for. This chapter gives you those tools, explains *why* each
one works (so you can rebuild it from memory in an exam, without the internet), and shows the traps.

The tools are:

1. Divisibility, `//`, `%` and `divmod`, including what they do for negative numbers.
2. Primes: trial division, the sieve of Eratosthenes, the smallest-prime-factor sieve, factorisation, segmented sieve.
3. GCD and LCM: Euclid's algorithm, extended Euclid, linear equations in whole numbers, the Chinese remainder theorem.
4. Modular arithmetic: what you may and may not do under a modulus, fast exponentiation, modular inverses.
5. Counting: Pascal's triangle, factorials with inverse factorials, Legendre's formula, Euler's totient.
6. Bit manipulation: `&`, `|`, `^`, `~`, shifts, and the classic tricks.

Everything here is built from Python you already know: loops, lists, functions, integers. The only new library
functions are `math.isqrt`, `math.gcd`, `math.lcm`, `math.comb` and the three-argument `pow`; and for each one you
will first write the plain loop version and see why it works.

### What is different about Python integers

Most contest problems are written with C++ or Java in mind. There, an `int` has 32 bits and a `long long` has 64
bits. Numbers larger than about `9.2 * 10^18` silently **wrap around** (overflow), and many "math" problems are
designed around that: "print the answer modulo 1,000,000,007" exists so that the answer always fits in 64 bits.

Python does not overflow. An `int` grows as large as memory allows:

```python
print(2 ** 100)
print(2 ** 64 - 1)
print((3 ** 10000).bit_length(), "bits in 3^10000")
```
```text
1267650600228229401496703205376
18446744073709551615
15850 bits in 3^10000
```

So why do we still care about the modulus? Three reasons.

1. **The problem asks for it.** The judge compares your output with the answer *modulo* `10^9 + 7` (or `998244353`).
   If you print the exact huge number, you get "Wrong Answer". The modulus is part of the question.
2. **Big integers are slow.** A number with 1,000,000 digits takes real time to multiply. A loop that multiplies
   a running product 10^6 times without ever reducing it creates numbers with millions of digits, and the loop
   that "should" take a second takes minutes. Reducing modulo `m` after each step keeps every number small
   (below `10^9 + 7`, so below `2^30`), and each step costs a few tens of nanoseconds of arithmetic.
3. **Habits carry over.** If you later write C++ or Java, you must multiply two numbers below `10^9 + 7` in a
   64-bit type and reduce at once, because the product can reach about `10^18`. Practising the habit now costs
   nothing.

Let us measure reason 2. We compute `n!` for `n = 20000` two ways: exactly, and modulo `10^9 + 7` at every step.

```python
import time

MOD = 10**9 + 7
n = 20000

t = time.perf_counter()
exact = 1
for i in range(2, n + 1):
    exact *= i
t_exact = time.perf_counter() - t

t = time.perf_counter()
small = 1
for i in range(2, n + 1):
    small = small * i % MOD
t_small = time.perf_counter() - t

print("bits in exact 20000!:", exact.bit_length())
print("exact value mod MOD equals small:", exact % MOD == small)
print("reducing at every step was faster:", t_small < t_exact)
```
```text
bits in exact 20000!: 256909
exact value mod MOD equals small: True
reducing at every step was faster: True
```

The two answers agree (we will prove why in section 7), but one of them works with a number that has hundreds of
thousands of bits (see the printed size above). For `n = 10^6` the exact version is not just slower, it is unusable.

### The two famous moduli

You will meet these constantly:

- `MOD = 10**9 + 7 = 1_000_000_007`. A prime number. Any two numbers below it multiply to less than `2^60`, so
  the product fits in a signed 64-bit integer.
- `MOD = 998244353`. Also prime. It is popular in problems about polynomials and transforms because of its
  special structure, but for us it is just "another prime".

Both being **prime** matters a lot: it is what makes division possible (section 8). Remember this sentence:
*a prime modulus turns the remainders into a field where every non-zero number has an inverse.* We will unpack
it slowly.

## 2. Divisibility, `//`, `%` and `divmod`

### Divisibility

We say `a` **divides** `b` (written `a | b`) when `b = a * k` for some whole number `k`. In code: `b % a == 0`.
Here `a` is a **divisor** (or **factor**) of `b`, and `b` is a **multiple** of `a`.

A few facts you will use again and again:

- `1` divides everything. Every number divides itself. Everything divides `0` (since `0 = a * 0`).
- If `a | b` and `a | c`, then `a | (b + c)` and `a | (b - c)`. A common divisor of two numbers divides their
  sum and their difference. This one simple fact is the whole reason Euclid's algorithm works.
- If `a | b` and `b | c`, then `a | c`.
- The divisors of a number come in **pairs**: if `d | n`, so does `n // d`. For `n = 36`, the pairs are
  `(1, 36), (2, 18), (3, 12), (4, 9), (6, 6)`. In every pair, one member is at most `sqrt(n)` and the other is at
  least `sqrt(n)`. This is why trial division only needs to go up to `sqrt(n)`.

### Floor division and remainder

For whole numbers `a` and `b > 0`, there is exactly one way to write `a = b * q + r` with `0 <= r < b`.
Here `q = a // b` is the **quotient** and `r = a % b` is the **remainder**.

For positive numbers every language agrees. The trouble starts with negative numbers, and here Python differs from
C, C++ and Java:

- Python: `//` rounds **down** (towards minus infinity), and `a % b` always has the **sign of `b`**.
- C/C++/Java: `/` rounds **towards zero**, and `a % b` has the **sign of `a`**.

Both obey `a == (a // b) * b + a % b`, but they pick different `q`. See what Python does:

```python
for a, b in [(17, 5), (-17, 5), (17, -5), (-17, -5)]:
    q = a // b
    r = a % b
    print(f"a={a:>3} b={b:>2}  a//b={q:>2}  a%b={r:>2}  check: {q * b + r}")
```
```text
a= 17 b= 5  a//b= 3  a%b= 2  check: 17
a=-17 b= 5  a//b=-4  a%b= 3  check: -17
a= 17 b=-5  a//b=-4  a%b=-3  check: 17
a=-17 b=-5  a//b= 3  a%b=-2  check: -17
```

Look at the row `a = -17, b = 5`. Python says `-17 // 5 = -4` (the floor of `-3.4`) and `-17 % 5 = 3`.
C++ would say `-3` and `-2`. For modular arithmetic Python's behaviour is a gift: **`x % m` with a positive `m`
is always in `0 .. m-1`**, even if `x` is negative. So `(a - b) % m` is safe without any extra fixing, and you do
not need the C++ idiom `((a - b) % m + m) % m`.

### divmod

`divmod(a, b)` returns the pair `(a // b, a % b)` in one call:

```python
q, r = divmod(100, 7)
print(q, r)
minutes = 275
hours, mins = divmod(minutes, 60)
print(hours, "h", mins, "min")
print(divmod(-7, 2))
```
```text
14 2
4 h 35 min
(-4, 1)
```

`divmod` is the right tool whenever you need both parts, for example to split an index in a flattened grid into
`(row, column)`, or to turn a total into hours and minutes.

**Try it 1: predict the output (negative numbers)**

```python
print(-7 // 2, -7 % 2)
print(7 // -2, 7 % -2)
print(-8 % 4, 8 % -4)
print(divmod(-1, 10))
print((-3) % 7 == 4)
```

Think about floor first: `-7 / 2 = -3.5`, floor is `-4`. Then `r = a - q*b`. Write down your answers before you open this.

<details><summary>Answer</summary>

```text
-4 1
-4 -1
0 0
(-1, 9)
True
```

`-7 // 2 = -4` and `-7 - (-4)(2) = 1`. For `7 // -2 = -4` (floor of `-3.5`) and `7 - (-4)(-2) = -1`: the
remainder takes the sign of the divisor `-2`. `-8 % 4` and `8 % -4` are both `0`. `divmod(-1, 10) = (-1, 9)`
because `-1 = 10 * (-1) + 9`. And `-3 % 7 = 4`, so the last line prints `True`.
</details>

### Digits with `%` and `//`

Two classic uses: `n % 10` is the last decimal digit and `n // 10` removes it. And `n % 2 == 0` tests for even.

```python
n = 90210
digits = []
while n > 0:
    digits.append(n % 10)
    n //= 10
print(digits, sum(digits))
```
```text
[0, 1, 2, 0, 9] 12
```

The same idea in base 2 gives the bits of a number (`n % 2`, `n // 2`), which links to section 10.

### How many divisors does a number have? (the plain way)

Count every `d` from `1` to `n` with `n % d == 0`. That is O(n) per number. It is the baseline we will beat.

```python
def count_divisors_slow(n):
    count = 0
    for d in range(1, n + 1):
        if n % d == 0:
            count += 1
    return count

print([count_divisors_slow(n) for n in range(1, 21)])
print(count_divisors_slow(360))
```
```text
[1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6]
24
```

With `n` up to `10^6` and many queries this is far too slow. After you have the pair idea and the sieve, you will
do it much faster. Hold that thought.

## 3. Primes and trial division

A **prime** is a whole number greater than 1 whose only divisors are 1 and itself. `2, 3, 5, 7, 11, 13, ...`.
Note: `1` is **not** prime (it has only one divisor), and `2` is the only even prime. A number greater than 1 that
is not prime is **composite**.

Primes matter because of the **fundamental theorem of arithmetic**: every whole number greater than 1 can be
written as a product of primes in exactly one way (ignoring order). For example `360 = 2^3 * 3^2 * 5`. Primes are
the atoms of numbers, and many problems become easy once you write the numbers in terms of their atoms.

### The simplest primality test

`n` is prime if no `d` in `2 .. n-1` divides it. That is O(n). We can do much better using the divisor pairs.

**Why only up to `sqrt(n)`?** Suppose `n = a * b` with `1 < a <= b`. Then `a * a <= a * b = n`, so `a <= sqrt(n)`.
So if `n` is composite, it has a divisor in `2 .. sqrt(n)`. If we find none up to there, no divisor exists and
`n` is prime. The cost drops from O(n) to O(sqrt n): for `n = 10^9`, from a billion steps to about 31,623.

### Writing the loop: avoid floats

Beginners write `for d in range(2, int(n ** 0.5) + 1)`. For huge `n` the float `n ** 0.5` can be off by one,
because floats have only 53 bits of precision. Two safe alternatives:

```python
import math

def is_prime_a(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:          # no square root at all
        if n % d == 0:
            return False
        d += 1
    return True

def is_prime_b(n):
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):   # isqrt: exact integer square root
        if n % d == 0:
            return False
    return True

print([n for n in range(30) if is_prime_a(n)])
print(is_prime_a(999_999_937), is_prime_b(999_999_937))
print(math.isqrt(99), math.isqrt(100), math.isqrt(10**18 - 1))
```
```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
True True
9 10 999999999
```

`math.isqrt(n)` returns the largest integer `r` with `r * r <= n`. It is exact for any size of `n`. The `d * d <= n`
loop is the same idea written by hand, and it is the form you will see in most solutions.

A cheap speed-up: handle `2` separately and then try only odd `d`. That halves the work.

```python
def is_prime_fast(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

print(is_prime_fast(2), is_prime_fast(1), is_prime_fast(97), is_prime_fast(10**9 + 7))
```
```text
True False True True
```

### Tracing the loop

Here is the test with a print at each step, so you can see it stop early for composites and run all the way for
primes.

```python
def trace_prime(n):
    print(f"testing {n}")
    d = 2
    while d * d <= n:
        if n % d == 0:
            print(f"  d={d}: {n} % {d} == 0 -> composite")
            return
        print(f"  d={d}: {n} % {d} = {n % d}")
        d += 1
    print(f"  d={d}: {d}*{d} > {n}, stop -> prime")

trace_prime(91)
trace_prime(29)
```
```text
testing 91
  d=2: 91 % 2 = 1
  d=3: 91 % 3 = 1
  d=4: 91 % 4 = 3
  d=5: 91 % 5 = 1
  d=6: 91 % 6 = 1
  d=7: 91 % 7 == 0 -> composite
testing 29
  d=2: 29 % 2 = 1
  d=3: 29 % 3 = 2
  d=4: 29 % 4 = 1
  d=5: 29 % 5 = 4
  d=6: 6*6 > 29, stop -> prime
```

Notice that `91 = 7 * 13` was caught at `d = 7`, the smaller of the pair, and that we never tested `13`.

**Try it 2: predict the number of loop steps**

How many times does the body of `while d * d <= n` run when `n = 10**9 + 7` (a prime) and `d` steps by 1 from 2?
And for `n = 10**9 + 7` stepping by 2 from 3? Estimate first, then check by running.

<details><summary>Answer</summary>

```python
n = 10**9 + 7
steps1 = 0
d = 2
while d * d <= n:
    steps1 += 1
    d += 1
steps2 = 0
d = 3
while d * d <= n:
    steps2 += 1
    d += 2
print(steps1, steps2)
```
```text
31621 15810
```

About 31,622 and 15,810: `sqrt(10^9) ~ 31,623`, half of it for the odd-only version. Even with 10^5 queries of
this size, the total is around `3 * 10^9` steps, which is too slow for Python. That is one reason we will learn the
sieve.
</details>

### Trial division for factorisation

The same loop factorises a number. Divide out each factor `d` as many times as possible; when `d * d > n`,
whatever is left (if greater than 1) is itself a prime.

```python
def factorise(n):
    factors = []                      # list of (prime, exponent)
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            factors.append((d, e))
        d += 1
    if n > 1:                          # leftover prime bigger than sqrt of what remains
        factors.append((n, 1))
    return factors

print(factorise(360))
print(factorise(97))
print(factorise(2 * 3 * 5 * 7 * 11 * 13))
print(factorise(10**12))
print(factorise(999_999_999_989))
```
```text
[(2, 3), (3, 2), (5, 1)]
[(97, 1)]
[(2, 1), (3, 1), (5, 1), (7, 1), (11, 1), (13, 1)]
[(2, 12), (5, 12)]
[(999999999989, 1)]
```

Two details worth noticing. First, the condition `d * d <= n` uses the *shrinking* `n`: after dividing out small
primes, the loop can stop earlier. Second, composite `d` never divides, because by the time we reach `d = 4` all
factors of 2 are gone (and so on). So `d` only ever "hits" primes, even though we try every number.

**Cost:** O(sqrt n) per number. For `n <= 10^12` that is up to `10^6` steps, fine for a few numbers. For many
numbers, we need a sieve.

### Divisor count and sum from the factorisation

If `n = p1^e1 * p2^e2 * ... * pk^ek`, every divisor chooses an exponent `0..e1` for `p1`, `0..e2` for `p2`, and so
on. So

```text
number of divisors = (e1 + 1) * (e2 + 1) * ... * (ek + 1)
```

For `360 = 2^3 * 3^2 * 5^1`: `(3 + 1)(2 + 1)(1 + 1) = 24`. Check it with the slow counter from before:

```python
def factorise(n):
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            factors.append((d, e))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors

def divisor_count(n):
    result = 1
    for p, e in factorise(n):
        result *= e + 1
    return result

def count_divisors_slow(n):
    return sum(1 for d in range(1, n + 1) if n % d == 0)

print(divisor_count(360), count_divisors_slow(360))
print(all(divisor_count(n) == count_divisors_slow(n) for n in range(1, 500)))
```
```text
24 24
True
```

Also, a number is a **perfect square** exactly when every exponent is even, which is exactly when its divisor
count is odd (the pair `(d, n // d)` collapses to one divisor `d = sqrt n`).

**Try it 3: factorise by hand, then check**

Factorise `5040`, `1001` and `65536` by hand. Then predict how many divisors each has.

<details><summary>Answer</summary>

```python
def factorise(n):
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            factors.append((d, e))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors

for n in [5040, 1001, 65536]:
    f = factorise(n)
    count = 1
    for p, e in f:
        count *= e + 1
    print(n, f, count)
```
```text
5040 [(2, 4), (3, 2), (5, 1), (7, 1)] 60
1001 [(7, 1), (11, 1), (13, 1)] 8
65536 [(2, 16)] 17
```

`5040 = 2^4 * 3^2 * 5 * 7`, so `5 * 3 * 2 * 2 = 60` divisors. `1001 = 7 * 11 * 13` gives 8. `65536 = 2^16` gives 17.
</details>


## 4. The sieve of Eratosthenes

### The idea: cross off instead of test

Trial division asks the question "is *this* number prime?" one number at a time. If you need **all** primes up
to `n`, or the answer for a hundred thousand different numbers, testing each one separately wastes work. The sieve
turns the question around: *cross off the multiples of each prime*. Whatever is never crossed off is prime.

Walk through it for `n = 30`:

1. Write `2 .. 30`. Nothing is crossed off yet.
2. The smallest uncrossed number is `2`. It is prime. Cross off `4, 6, 8, ..., 30`.
3. The next uncrossed number is `3`. Prime. Cross off `6, 9, 12, ...`.
4. The next is `5`. Prime. Cross off `10, 15, 20, 25, 30`.
5. The next is `7`, and so on. Everything left is prime.

### Why start crossing at `p * p`

When we process the prime `p`, the multiples `2p, 3p, ..., (p-1)p` have a smaller factor than `p`
(namely 2, 3, ..., p-1), so an earlier prime has already crossed them off. The first multiple that could still be
fresh is `p * p`. So we start there. And since `p * p` must be at most `n`, we only process primes up to
`sqrt(n)`: a composite number `m <= n` always has a prime factor `<= sqrt(m) <= sqrt(n)`, and that factor crosses
it off.

```python
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = False
    if n >= 1:
        is_prime[1] = False
    p = 2
    while p * p <= n:
        if is_prime[p]:
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
        p += 1
    return is_prime

flags = sieve(50)
print([i for i, ok in enumerate(flags) if ok])
```
```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

### Seeing it work

Let us print what each prime crosses off, for `n = 50`. Only *new* crossings are shown; a number such as 12
is crossed by `2` and again by `3`, but only the first counts.

```python
n = 50
crossed = [False] * (n + 1)
p = 2
while p * p <= n:
    if not crossed[p]:
        new = []
        for m in range(p * p, n + 1, p):
            if not crossed[m]:
                crossed[m] = True
                new.append(m)
        print(f"p={p}: starts at {p * p}, newly crossed {new}")
    p += 1
print("primes:", [i for i in range(2, n + 1) if not crossed[i]])
```
```text
p=2: starts at 4, newly crossed [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50]
p=3: starts at 9, newly crossed [9, 15, 21, 27, 33, 39, 45]
p=5: starts at 25, newly crossed [25, 35]
p=7: starts at 49, newly crossed [49]
primes: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

Look at `p = 3`: it starts at `9`, not `6`, because `6` was crossed off by `2`. And `p = 5` starts at `25`; `5 * 5 = 25
<= 50`, but `p = 11` would start at `121 > 50`, so the loop stops at `p = 7`.

### Cost

For each prime `p` we do about `n / p` crossings, so the total is
`n * (1/2 + 1/3 + 1/5 + 1/7 + ...)`. The sum of `1/p` over primes up to `n` grows like `log log n`, which is
below 4 for any `n` you will ever use. The sieve is **O(n log log n)** time and **O(n)** space: nearly linear.

### Faster in Python: slice assignment and `bytearray`

The inner loop `for multiple in range(p * p, n + 1, p)` is a Python-level loop, about `n log log n` iterations,
which for `n = 5 * 10^6` is slow-ish in CPython. A very common speed-up assigns a whole slice at once, which runs
in C:

```python
import time

def sieve_loop(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p <= n:
        if is_prime[p]:
            for m in range(p * p, n + 1, p):
                is_prime[m] = False
        p += 1
    return is_prime

def sieve_slice(n):
    is_prime = bytearray([1]) * (n + 1)     # one byte per number
    is_prime[0] = is_prime[1] = 0
    p = 2
    while p * p <= n:
        if is_prime[p]:
            is_prime[p * p::p] = bytes(len(range(p * p, n + 1, p)))   # zeros
        p += 1
    return is_prime

n = 2_000_000
t = time.perf_counter(); a = sieve_loop(n); t1 = time.perf_counter() - t
t = time.perf_counter(); b = sieve_slice(n); t2 = time.perf_counter() - t
print("same primes:", [i for i in range(n + 1) if a[i]] == [i for i in range(n + 1) if b[i]])
print("number of primes below 2,000,000:", sum(b))
print("slice version faster:", t2 < t1)
```
```text
same primes: True
number of primes below 2,000,000: 148933
slice version faster: True
```

`bytearray([1]) * (n + 1)` makes `n + 1` bytes all equal to 1; `bytes(k)` makes `k` zero bytes. The slice
`is_prime[p*p::p]` is every `p`-th byte from `p * p` onward, and we replace all of them with zeros in one go. The
right-hand side must have **exactly** the same length as the slice, which is why we compute
`len(range(p * p, n + 1, p))`. Memory drops too: a bytearray uses 1 byte per entry, a list of booleans 8.

Counting primes is then `sum(is_prime)`, and listing them is `[i for i in range(n + 1) if is_prime[i]]`.

**Try it 4: sieve boundaries**

What does `sieve(0)`, `sieve(1)` and `sieve(2)` return in the first version above? Which line protects against an
`IndexError`? Predict, then check.

<details><summary>Answer</summary>

```python
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = False
    if n >= 1:
        is_prime[1] = False
    p = 2
    while p * p <= n:
        if is_prime[p]:
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
        p += 1
    return is_prime

print(sieve(0), sieve(1), sieve(2))
```
```text
[False] [False, False] [False, False, True]
```

The guard `if n >= 1` is needed because for `n = 0` the list has a single entry, and `is_prime[1]` would raise
`IndexError`. Small edge cases such as `n = 0, 1, 2` are exactly where sieve solutions break in tests.
</details>

### Segmented sieve

What if `n` is `10^10`? An array of ten billion bytes is out of the question. But often we only need the primes in a
**window** `[L, R]` with `R - L` at most about `10^6`. Here is the trick:

1. Every composite `m <= R` has a prime factor `<= sqrt(R)`. For `R = 10^10`, that is `<= 10^5`.
2. So: first sieve normally up to `isqrt(R)` (small, 10^5 entries) to get the **small primes**.
3. Make a flag array for the window, index `i` standing for the number `L + i`.
4. For each small prime `p`, cross off its multiples in the window. The first multiple `>= L` is
   `max(p * p, ((L + p - 1) // p) * p)`. We take `max` with `p * p` so that `p` itself, if it lies in the window,
   is not crossed off.
5. Numbers `< 2` are not prime (careful if `L` is 0 or 1).

```python
import math

def small_sieve(n):
    flags = bytearray([1]) * (n + 1)
    flags[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(n) + 1):
        if flags[p]:
            flags[p * p::p] = bytes(len(range(p * p, n + 1, p)))
    return [i for i in range(n + 1) if flags[i]]

def segmented(L, R):
    size = R - L + 1
    window = bytearray([1]) * size
    for p in small_sieve(math.isqrt(R) + 1):
        start = max(p * p, ((L + p - 1) // p) * p)
        if start > R:
            continue
        window[start - L::p] = bytes(len(range(start - L, size, p)))
    for x in range(L, min(2, R + 1)):      # 0 and 1 are not prime
        window[x - L] = 0
    return [L + i for i in range(size) if window[i]]

print(segmented(10, 50))
print(segmented(0, 20))
print(segmented(10**10 - 100, 10**10))
```
```text
[11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
[2, 3, 5, 7, 11, 13, 17, 19]
[9999999929, 9999999943, 9999999967]
```

The cost is `O((R - L) log log R + sqrt(R))`: we pay for the window and for the small primes, never for the whole range
`1 .. R`. The same code works with `L = 1`.

### The smallest-prime-factor (SPF) sieve

The plain sieve says "prime or not". A small change stores *why*: for each number, its **smallest prime factor**.
Then any number up to `n` is factorised in O(log n) steps by repeatedly dividing by its smallest prime factor.

```python
def build_spf(n):
    spf = list(range(n + 1))                 # spf[i] = i at first (a prime is its own smallest factor)
    p = 2
    while p * p <= n:
        if spf[p] == p:                      # p is prime
            for m in range(p * p, n + 1, p):
                if spf[m] == m:              # not yet claimed by a smaller prime
                    spf[m] = p
        p += 1
    return spf

def factorise_spf(x, spf):
    result = []
    while x > 1:
        p = spf[x]
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        result.append((p, e))
    return result

spf = build_spf(100)
print(spf[:21])
print(factorise_spf(84, spf))
print(factorise_spf(97, spf))
print(factorise_spf(96, spf))
```
```text
[0, 1, 2, 3, 2, 5, 2, 7, 2, 3, 2, 11, 2, 13, 2, 3, 2, 17, 2, 19, 2]
[(2, 2), (3, 1), (7, 1)]
[(97, 1)]
[(2, 5), (3, 1)]
```

Read `spf[:21]`: `spf[12] = 2`, `spf[15] = 3`, `spf[7] = 7` (a prime points to itself). The test
`if spf[m] == m` makes sure a number keeps the **smallest** prime that reached it, since primes are processed
in increasing order.

Build once in O(n log log n), then each query is O(log n). That turns "divisor count for 10^5 queries with values up to
10^6" from impossible (10^5 * 10^3 steps) into easy.

```python
def build_spf(n):
    spf = list(range(n + 1))
    p = 2
    while p * p <= n:
        if spf[p] == p:
            for m in range(p * p, n + 1, p):
                if spf[m] == m:
                    spf[m] = p
        p += 1
    return spf

def divisor_count(x, spf):
    result = 1
    while x > 1:
        p = spf[x]
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        result *= e + 1
    return result

spf = build_spf(1000)
print([divisor_count(x, spf) for x in [1, 12, 36, 97, 360, 720, 997]])
```
```text
[1, 6, 9, 2, 24, 30, 2]
```

### Counting divisors of *every* number: the divisor sieve

If you need the divisor count of **all** numbers up to `n`, the "cross off" pattern works again. For every `d`, add
1 to each multiple of `d`:

```python
n = 20
count = [0] * (n + 1)
for d in range(1, n + 1):
    for multiple in range(d, n + 1, d):
        count[multiple] += 1
print(count[1:])
```
```text
[1, 2, 2, 3, 2, 4, 2, 4, 3, 4, 2, 6, 2, 4, 4, 5, 2, 6, 2, 6]
```

This is O(n log n) in total (the harmonic sum `n/1 + n/2 + ... + n/n`), and it is the same count as the
earlier loop, only organised by divisor rather than by number. The same shape computes the *sum* of divisors,
or `phi` (section 9).

**Try it 5: write the SPF-based prime check**

Using `build_spf`, how would you test "is `x` prime?" for `2 <= x <= n` in O(1)? Then check your answer.

<details><summary>Answer</summary>

```python
def build_spf(n):
    spf = list(range(n + 1))
    p = 2
    while p * p <= n:
        if spf[p] == p:
            for m in range(p * p, n + 1, p):
                if spf[m] == m:
                    spf[m] = p
        p += 1
    return spf

spf = build_spf(30)
print([x for x in range(2, 31) if spf[x] == x])
```
```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

`x` is prime exactly when `spf[x] == x`. So the SPF array contains the plain sieve as a by-product.
</details>

### Which prime tool when?

| You need | Use | Cost |
|---|---|---|
| Is this one number prime? (n up to ~10^12) | trial division to sqrt | O(sqrt n) |
| Factorise one number up to ~10^12 | trial division | O(sqrt n) |
| All primes up to n (n up to ~10^7) | sieve | O(n log log n) |
| Factorise many numbers up to ~10^6 or 10^7 | SPF sieve | O(n log log n) + O(log n) each |
| Primes in `[L, R]` with `R` huge, window small | segmented sieve | O(window log log R + sqrt R) |
| Divisor counts of all numbers up to n | divisor sieve | O(n log n) |

## 5. GCD and LCM

### What they are

The **greatest common divisor** `gcd(a, b)` is the largest number that divides both `a` and `b`. The **least
common multiple** `lcm(a, b)` is the smallest positive number that both divide. Examples: `gcd(12, 18) = 6`,
`lcm(12, 18) = 36`. Two numbers with `gcd = 1` are called **coprime**.

GCD shows up when you simplify fractions (`12/18 = 2/3`), when you ask "when do two cycles line up?" (that is
the LCM), and as a hidden building block in dozens of problems.

Special cases to remember: `gcd(a, 0) = a` (everything divides 0, so the largest common divisor of `a` and `0` is `a`),
and `gcd(0, 0) = 0` by convention.

### Euclid's algorithm

The slow way is to test every candidate. The fast way, more than 2,000 years old, is:

```text
gcd(a, b) = gcd(b, a % b)        and        gcd(a, 0) = a
```

**Why it works.** Write `a = q * b + r` with `r = a % b`. Any number `d` that divides both `a` and `b` also divides
`a - q * b = r` (a difference of multiples of `d`). So `d` is a common divisor of `b` and `r`. Conversely, any
common divisor of `b` and `r` divides `q * b + r = a`. The two pairs `(a, b)` and `(b, r)` have **exactly the
same set of common divisors**, so they have the same greatest one. And `r < b`, so the numbers keep shrinking
until `r = 0`; at that point `gcd(a, 0) = a`.

```python
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

print(gcd(12, 18), gcd(18, 12), gcd(7, 13), gcd(0, 5), gcd(5, 0), gcd(0, 0), gcd(100, 100))
```
```text
6 6 1 5 5 0 100
```

Note that `gcd(12, 18)` and `gcd(18, 12)` agree: the first step with `a < b` just swaps them
(`12 % 18 = 12`, so `(12, 18)` becomes `(18, 12)`).

### Tracing it

```python
def gcd_trace(a, b):
    print(f"gcd({a}, {b})")
    while b != 0:
        print(f"  a={a}, b={b}: {a} = {a // b} * {b} + {a % b}")
        a, b = b, a % b
    print(f"  b is 0 -> answer {a}")
    return a

gcd_trace(252, 105)
gcd_trace(17, 5)
```
```text
gcd(252, 105)
  a=252, b=105: 252 = 2 * 105 + 42
  a=105, b=42: 105 = 2 * 42 + 21
  a=42, b=21: 42 = 2 * 21 + 0
  b is 0 -> answer 21
gcd(17, 5)
  a=17, b=5: 17 = 3 * 5 + 2
  a=5, b=2: 5 = 2 * 2 + 1
  a=2, b=1: 2 = 2 * 1 + 0
  b is 0 -> answer 1
```

### Why it is fast

The remainder at least halves every **two** steps: after one step, `a % b < b` and if `b <= a / 2` the
remainder is smaller than `a/2`, otherwise `a % b = a - b < a / 2`. Either way, within two steps the larger number
at least halves. So Euclid takes at most about `2 * log2(min(a, b))` steps, and for numbers near `10^18` that is under
about 90 steps. The worst case is consecutive Fibonacci numbers:

```python
def gcd_steps(a, b):
    steps = 0
    while b != 0:
        a, b = b, a % b
        steps += 1
    return a, steps

fib = [1, 1]
while len(fib) < 90:
    fib.append(fib[-1] + fib[-2])
print(gcd_steps(fib[88], fib[87]))
print(gcd_steps(10**18, 10**18 - 1))
print(gcd_steps(10**18, 10**9))
```
```text
(1, 87)
(1, 2)
(1000000000, 1)
```

### LCM from GCD

The key identity is `gcd(a, b) * lcm(a, b) = a * b` (for positive numbers). Why: in terms of prime exponents, GCD takes
the **minimum** exponent for each prime and LCM takes the **maximum**, and `min + max = sum` of the two exponents.
So

```text
lcm(a, b) = a * b // gcd(a, b)  =  a // gcd(a, b) * b
```

The second form matters in C++ (it avoids an overflow in the product `a * b`). In Python there is no overflow, but
dividing first still keeps numbers small, so it is a good habit.

```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return a // gcd(a, b) * b

print(lcm(12, 18), lcm(4, 6), lcm(7, 13), lcm(0, 5), lcm(10**18, 10**18 - 1) == 10**18 * (10**18 - 1))
```
```text
36 12 91 0 True
```

### GCD of many numbers, LCM of many numbers

Both are **associative**: `gcd(a, b, c) = gcd(gcd(a, b), c)`. So fold across the list. LCM works the same way, but
it can grow very fast: `lcm(1..40)` is already `5342931457063200`. If you need `lcm(1..n)` modulo something, you cannot
take `lcm` of residues (the identity `a // g * b` needs exact values). Use prime powers instead:

`lcm(1..n) = product over primes p <= n of p^k`, where `p^k` is the largest power of `p` that is `<= n`.

```python
import math
from functools import reduce

values = [12, 18, 30, 42]
print(reduce(math.gcd, values), reduce(math.lcm, values))

def lcm_upto(n):
    # product of the largest power of each prime <= n
    flags = bytearray([1]) * (n + 1)
    result = 1
    for p in range(2, n + 1):
        if flags[p]:
            for m in range(p * p, n + 1, p):
                flags[m] = 0
            power = p
            while power * p <= n:
                power *= p
            result *= power
    return result

print(lcm_upto(10), reduce(math.lcm, range(1, 11)))
print(lcm_upto(40), reduce(math.lcm, range(1, 41)))
print(lcm_upto(40) % (10**9 + 7))
```
```text
6 1260
2520 2520
5342931457063200 5342931457063200
419662683
```

`reduce(f, items)` is `f(f(f(a0, a1), a2), a3)`. It is the same as a loop with a running value. `math.gcd` and
`math.lcm` also accept several arguments directly (`math.gcd(12, 18, 30)`) in modern Python, and `math.lcm` returns 0 if any
argument is 0.

For `lcm(1..n) mod m` with `n = 10^6`, use the sieve version and multiply `power % m` into the result. Each factor is
a small number, and you never build the giant exact LCM. This is the typical "counting under a modulus" move.

**Try it 6: trace Euclid by hand**

Compute `gcd(1071, 462)` on paper, writing each `a = q*b + r` line. Then compute `lcm(1071, 462)` using the identity.
Check with `math`.

<details><summary>Answer</summary>

```python
import math
a, b = 1071, 462
x, y = a, b
while y:
    print(f"{x} = {x // y} * {y} + {x % y}")
    x, y = y, x % y
print("gcd", x, "lcm", a // x * b, "math:", math.gcd(a, b), math.lcm(a, b))
```
```text
1071 = 2 * 462 + 147
462 = 3 * 147 + 21
147 = 7 * 21 + 0
gcd 21 lcm 23562 math: 21 23562
```

The last non-zero remainder is the gcd.
</details>

**Try it 7: gcd and negative numbers**

`math.gcd(-12, 18)` returns what? What does the hand-written `gcd` loop above give for `(-12, 18)` and `(12, -18)`?
Predict, then run.

<details><summary>Answer</summary>

```python
import math

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

print(math.gcd(-12, 18), math.gcd(12, -18), math.gcd(-12, -18))
print(gcd(-12, 18), gcd(12, -18))
```
```text
6 6 6
6 -6
```

`math.gcd` always returns a non-negative number. The hand-written loop can return a negative gcd because Python's `%` takes
the sign of the divisor. If negative inputs are possible, apply `abs` first or at the end.
</details>

## 6. Extended Euclid, linear equations and the Chinese remainder theorem

### Bezout's identity

Euclid's algorithm does more than find `g = gcd(a, b)`. You can run it **backwards** to find whole numbers `x` and `y`
(possibly negative) such that

```text
a * x + b * y = g
```

This is **Bezout's identity**. It is hugely useful: it gives modular inverses, solves equations in whole numbers,
and is the engine of the Chinese remainder theorem. Do not be put off by the name, it is a few lines.

### Deriving the recursion

Suppose we already know `x', y'` for the smaller pair `(b, a % b)`:

```text
b * x' + (a % b) * y' = g
```

Write `a % b = a - (a // b) * b`. Substitute:

```text
b * x' + (a - (a // b) * b) * y' = g
a * y' + b * (x' - (a // b) * y') = g
```

So for the pair `(a, b)` we may take `x = y'` and `y = x' - (a // b) * y'`. The base case is `b = 0`: `gcd(a, 0) = a`,
so `a * 1 + 0 * 0 = a` and `x = 1, y = 0`.

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

for a, b in [(30, 12), (17, 5), (240, 46), (5, 0), (0, 7)]:
    g, x, y = ext_gcd(a, b)
    print(f"a={a} b={b}: g={g} x={x} y={y}  check {a}*{x} + {b}*{y} = {a * x + b * y}")
```
```text
a=30 b=12: g=6 x=1 y=-2  check 30*1 + 12*-2 = 6
a=17 b=5: g=1 x=-2 y=7  check 17*-2 + 5*7 = 1
a=240 b=46: g=2 x=-9 y=47  check 240*-9 + 46*47 = 2
a=5 b=0: g=5 x=1 y=0  check 5*1 + 0*0 = 5
a=0 b=7: g=7 x=0 y=1  check 0*0 + 7*1 = 7
```

The recursion depth is only about `log(min(a, b))`, so it is safe. An **iterative** version, which tracks the
coefficients in a small table, is also standard, and is what the "table" trace problem uses:

```python
def ext_gcd_iter(a, b):
    old_r, r = a, b
    old_s, s = 1, 0        # a = old_s * a + 0 * b
    old_t, t = 0, 1        # b = 0 * a + 1 * b
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t

print(ext_gcd_iter(240, 46))
print(ext_gcd_iter(30, 12))
```
```text
(2, -9, 47)
(6, 1, -2)
```

The invariant: at every step each remainder is a combination of the originals, `r = s * a + t * b`. Initially
`a = 1*a + 0*b` and `b = 0*a + 1*b`. When we form the new remainder `old_r - q * r`, we form the matching `s` and `t`
in the same way, so the invariant is kept. When `r` reaches 0, `old_r` is the gcd and `old_s, old_t` the coefficients.

Here is the full table for `a = 240, b = 46`:

```python
a, b = 240, 46
old_r, r = a, b
old_s, s = 1, 0
old_t, t = 0, 1
print(f"{'q':>3} {'r':>4} {'s':>4} {'t':>4}")
print(f"{'-':>3} {old_r:>4} {old_s:>4} {old_t:>4}")
print(f"{'-':>3} {r:>4} {s:>4} {t:>4}")
while r != 0:
    q = old_r // r
    old_r, r = r, old_r - q * r
    old_s, s = s, old_s - q * s
    old_t, t = t, old_t - q * t
    print(f"{q:>3} {r:>4} {s:>4} {t:>4}")
print("gcd =", old_r, "x =", old_s, "y =", old_t)
```
```text
  q    r    s    t
  -  240    1    0
  -   46    0    1
  5   10    1   -5
  4    6   -4   21
  1    4    5  -26
  1    2   -9   47
  2    0   23 -120
gcd = 2 x = -9 y = 47
```

Each printed row after the first two shows the *new* `(r, s, t)`; the row before the final zero holds the answer. Check:
`240 * (-9) + 46 * 47 = -2160 + 2162 = 2`.

### Solving `a x + b y = c` (a linear Diophantine equation)

A **Diophantine** equation just means "we want whole-number solutions". For `a x + b y = c`:

- `a x + b y` is always a multiple of `g = gcd(a, b)`. So if `g` does **not** divide `c`, there is **no** solution.
- If `g | c`: get `a x0 + b y0 = g` from extended Euclid, then multiply by `c // g`:
  `x = x0 * (c // g)`, `y = y0 * (c // g)`.
- All other solutions are `x + k * (b // g)`, `y - k * (a // g)` for any whole `k`. (Adding `b/g` to `x` adds
  `a * b / g` to `a x`, and the `y` change removes exactly that.)

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def diophantine(a, b, c):
    g, x0, y0 = ext_gcd(a, b)
    if c % g != 0:
        return None
    k = c // g
    return x0 * k, y0 * k, b // g, a // g

print(diophantine(6, 9, 15))
print(diophantine(6, 9, 10))
x, y, dx, dy = diophantine(6, 9, 15)
for k in range(-2, 3):
    X, Y = x + k * dx, y - k * dy
    print(k, X, Y, 6 * X + 9 * Y)
```
```text
(-5, 5, 3, 2)
None
-2 -11 9 15
-1 -8 7 15
0 -5 5 15
1 -2 3 15
2 1 1 15
```

A practical story: you have coins of 6 and 9 and want to pay exactly 15; negative solutions mean "give change back". Asking for
*non-negative* solutions needs one more step (pick `k` in the right range), which you can do with ceilings and floors.

### Modular inverse (preview)

If `gcd(a, m) = 1`, then `a x + m y = 1` for some `x, y`. Take both sides modulo `m`: `a x == 1 (mod m)`. So `x % m` is
the **modular inverse** of `a`. This is the main use of extended Euclid. We return to it in section 8.

### Linear congruences `a x == b (mod m)`

This means: find `x` such that `m` divides `a x - b`, i.e. `a x - b = m * y`, i.e. `a x - m y = b`. That is a
Diophantine equation, so:

- Let `g = gcd(a, m)`. If `g` does **not** divide `b`, there is **no** solution. (The left side `a x mod m` can only be
  multiples of `g`.)
- If `g | b`: divide everything by `g`. Now `(a/g) x == (b/g) (mod m/g)` with `gcd(a/g, m/g) = 1`, so `a/g` has an
  inverse modulo `m/g`: `x0 = (b/g) * inv(a/g, m/g) mod (m/g)`.
- There are exactly **`g` solutions** modulo `m`: `x0, x0 + m/g, x0 + 2m/g, ..., x0 + (g-1) m/g`. The smallest non-negative
  one is `x0` itself.

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def solve_congruence(a, b, m):
    # smallest x >= 0 with a*x % m == b % m, or None
    g = ext_gcd(a, m)[0]
    if b % g != 0:
        return None
    a2, b2, m2 = a // g, b // g, m // g
    _, inv, _ = ext_gcd(a2 % m2, m2)
    return (b2 * inv) % m2

print(solve_congruence(6, 4, 10))     # 6x = 4 mod 10
print(solve_congruence(6, 3, 10))     # no solution: gcd 2 does not divide 3
print(solve_congruence(3, 1, 7))
print([x for x in range(10) if 6 * x % 10 == 4])
```
```text
4
None
5
[4, 9]
```

In the first query `g = 2`, so there are two solutions modulo 10: `x0 = 4` and `x0 + 5 = 9`. The brute-force line confirms
`[4, 9]`; the smallest is 4.

### The Chinese remainder theorem (two congruences)

Problem: find `x` with `x == a1 (mod m1)` and `x == a2 (mod m2)`.

Write `x = a1 + m1 * t`. We need `a1 + m1 t == a2 (mod m2)`, i.e. `m1 t == a2 - a1 (mod m2)`, which is the linear
congruence we just learned to solve (with `a = m1`, `b = a2 - a1`, `m = m2`):

- Let `g = gcd(m1, m2)`. If `g` does not divide `a2 - a1`, there is **no** solution.
- Otherwise `t` exists, unique modulo `m2 / g`. Then `x = a1 + m1 * t` is a solution, unique modulo `lcm(m1, m2) = m1 // g * m2`.

If `m1` and `m2` are coprime, `g = 1`, a solution always exists, and it is unique modulo `m1 * m2`: this is the classical
statement. Contest problems often make the moduli **not** coprime, which is why we do the general version.

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def crt(a1, m1, a2, m2):
    g, p, _ = ext_gcd(m1, m2)
    if (a2 - a1) % g != 0:
        return None
    lcm = m1 // g * m2
    t = ((a2 - a1) // g * p) % (m2 // g)
    return (a1 + m1 * t) % lcm, lcm

print(crt(2, 3, 3, 5))     # x = 2 mod 3, x = 3 mod 5
print(crt(1, 4, 3, 6))     # moduli share a factor 2: 1 vs 3 differ by 2, OK
print(crt(1, 4, 2, 6))     # 1 vs 2 differ by 1, not divisible by 2: no solution
print(crt(0, 6, 4, 10))
```
```text
(8, 15)
(9, 12)
None
(24, 30)
```

The first answer, `(8, 15)`, means "`x = 8` and every number `8 + 15k`". Check: `8 % 3 = 2` and `8 % 5 = 3`. To combine more
than two congruences, fold: replace two congruences by their combined one `(x, lcm)` and combine that with the next.

**Try it 8: apply extended Euclid**

Find whole numbers `x, y` with `35 x + 15 y = 10`. Is there a solution to `35 x + 15 y = 12`?

<details><summary>Answer</summary>

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

g, x, y = ext_gcd(35, 15)
print(g, x, y, 35 * x + 15 * y)
print("scale to 10:", x * 10 // g, y * 10 // g, 35 * (x * 10 // g) + 15 * (y * 10 // g))
print("12 divisible by g?", 12 % g == 0)
```
```text
5 1 -2 5
scale to 10: 2 -4 10
12 divisible by g? False
```

`gcd(35, 15) = 5`. `5 | 10`, so scale by 2. `5` does not divide `12`, so `35 x + 15 y = 12` has no whole-number solution.
</details>

**Try it 9: solve a congruence by hand**

Solve `9 x == 12 (mod 15)`. How many solutions are there in `0 .. 14`? What is the smallest?

<details><summary>Answer</summary>

```python
sols = [x for x in range(15) if 9 * x % 15 == 12]
print(sols)
```
```text
[3, 8, 13]
```

`g = gcd(9, 15) = 3` divides 12, so there are 3 solutions, spaced `15 / 3 = 5` apart. Reduce: `3 x == 4 (mod 5)`, and
`3^{-1} = 2 (mod 5)`, so `x == 8 == 3 (mod 5)`. The smallest is 3.
</details>

**Try it 10: combine two congruences**

Find the smallest `x >= 0` with `x % 4 == 3` and `x % 9 == 5`. Do it by the formula, and also by brute force.

<details><summary>Answer</summary>

```python
x = next(x for x in range(4 * 9) if x % 4 == 3 and x % 9 == 5)
print(x)
```
```text
23
```

`m1 = 4, m2 = 9` are coprime, so exactly one solution exists in `0 .. 35`.
</details>


## 7. Modular arithmetic and fast exponentiation

### What "mod m" means

Two numbers are **congruent modulo m**, written `a == b (mod m)`, when `m` divides `a - b`; equivalently, they have the
same remainder when divided by `m`. Think of a clock: on a 12-hour clock, 15 o'clock *is* 3 o'clock. Numbers wrap around, and
we only care about which of the `m` positions we land on: `0, 1, ..., m - 1`.

The reason this is useful for counting is that **sums, differences and products survive the wrap-around**:

```text
(a + b) % m == ((a % m) + (b % m)) % m
(a - b) % m == ((a % m) - (b % m)) % m
(a * b) % m == ((a % m) * (b % m)) % m
```

**Proof for multiplication.** Write `a = m*s + r` and `b = m*t + u`, so `r = a % m`, `u = b % m`. Then
`a * b = m*m*s*t + m*s*u + m*t*r + r*u = m * (something) + r*u`. So `a * b` and `r * u` differ by a multiple of `m`:
same remainder. The same idea proves the other two rules.

The practical meaning: you may reduce **at any moment** during a sum, difference or product, and the final remainder is
identical. This is the trick that lets us work with the 77,000-digit number `20000!` without ever building it.

```python
import random
MOD = 1_000_003

ok = True
for _ in range(10000):
    a = random.randint(-10**12, 10**12)
    b = random.randint(-10**12, 10**12)
    if (a + b) % MOD != ((a % MOD) + (b % MOD)) % MOD:
        ok = False
    if (a - b) % MOD != ((a % MOD) - (b % MOD)) % MOD:
        ok = False
    if (a * b) % MOD != ((a % MOD) * (b % MOD)) % MOD:
        ok = False
print("all rules held on 10000 random pairs (negatives too):", ok)
```
```text
all rules held on 10000 random pairs (negatives too): True
```

The pattern for a running total under a modulus:

```python
MOD = 10**9 + 7

total = 0
for x in [10**18, 5, 10**18 + 3, 7]:
    total = (total + x) % MOD
print(total)

product = 1
for x in [123456789, 987654321, 555555555, 111111111]:
    product = product * x % MOD
print(product)
```
```text
113
579187588
```

### Python's friendly negative remainders

In the section on `//` and `%` we saw that `x % m` is never negative for positive `m`. So in subtraction, `(a - b) % m`
is already in `0 .. m-1`. In C++ you must write `((a - b) % m + m) % m`; in Python the plain form is correct, and it
is a typical source of bugs when you copy C++ code with the extra `+ m`. (The extra `+ m` is harmless in Python, just
unnecessary.)

### Division is different

Addition, subtraction and multiplication carry through. **Division does not.** Consider modulus `7` and `a = 14`, `b = 7`.
Here `a // b = 2`. But `a % 7 = 0` and `b % 7 = 0`, so `(a % 7) // (b % 7)` is a crash. A subtler example: mod 10,
`a = 24`, `b = 4`: `24 // 4 = 6`, while `(24 % 10) // (4 % 10) = 4 // 4 = 1`. They disagree.

```python
a, b, m = 24, 4, 10
print("true quotient mod m:", (a // b) % m)
print("divide the residues:", (a % m) // (b % m))
```
```text
true quotient mod m: 6
divide the residues: 1
```

The right idea is not "divide" but "multiply by the **inverse**" (section 8). A second warning: you cannot always cancel a
common factor either. `2 * 3 == 2 * 1 (mod 4)`, since both sides are `2` after reducing, yet `3 != 1 (mod 4)`.

### You cannot reduce exponents modulo m

`a ** b % m` is **not** `a ** (b % m) % m`. For example `2 ** 10 % 7 = 1024 % 7 = 2`, whereas `2 ** (10 % 7) % 7 = 2**3 % 7 = 1`.
(What *is* true: exponents can be reduced modulo `p - 1` when `m = p` is prime and `a` is not a multiple of `p`; see Fermat.)

```python
print(2 ** 10 % 7, 2 ** (10 % 7) % 7)
print(2 ** 10 % 7, 2 ** (10 % 6) % 7)      # reduce the exponent modulo p - 1 = 6
```
```text
2 1
2 2
```

### Fast exponentiation (binary exponentiation)

We want `a ** b % m` where `b` can be `10**18`. A loop that multiplies `b` times is hopeless. The idea:
**square repeatedly** and use the binary digits of `b`.

For example, `a ** 13`. In binary `13 = 1101 = 8 + 4 + 1`, so `a ** 13 = a**8 * a**4 * a**1`. And we get `a**1, a**2, a**4,
a**8` by squaring: each is the square of the previous. So about `log2(b)` squarings and at most `log2(b)` extra multiplications.

The formal rule, written recursively:

```text
power(a, 0) = 1
power(a, b) = power(a * a, b // 2)            if b is even
power(a, b) = a * power(a * a, b // 2)        if b is odd
```

Correct because `a ** b = (a * a) ** (b // 2)` when `b` is even, and one extra factor `a` when odd.

Iterative form (no recursion; the standard version):

```python
def power_mod(a, b, m):
    result = 1
    a %= m
    while b > 0:
        if b & 1:                    # lowest bit of b is 1
            result = result * a % m
        a = a * a % m                # square the base
        b >>= 1                      # move to the next bit of b
    return result % m

print(power_mod(2, 10, 1000), 2 ** 10 % 1000)
print(power_mod(3, 200, 13), pow(3, 200, 13))
print(power_mod(7, 10**18, 10**9 + 7))
print(power_mod(5, 0, 7), power_mod(0, 0, 7), power_mod(0, 5, 7))
print(power_mod(10, 5, 1))
```
```text
24 24
9 9
259616729
1 1 0
0
```

`b & 1` and `b >>= 1` are bit tricks you will meet in section 10; if they are new, read them as `b % 2 == 1` and `b //= 2`.

Two edge cases to know: `power_mod(5, 0, 7) = 1` (an empty product is 1), and with modulus `1` everything must be `0`, because every number is
`0 mod 1`. Look at the last line of the output: our `power_mod(10, 5, 1)` gives `0` only because the loop multiplies and reduces. For `b = 0` and `m = 1` the
loop never runs and it would return `1`, which is wrong. To be safe, `return result % m`.

### Tracing it

Let us watch `3 ** 13 mod 1000` step by step. In binary `13 = 1101`.

```python
a, b, m = 3, 13, 1000
result = 1
print(f"{'base':>6} {'exp':>4} {'bit':>4} {'result':>7}")
while b > 0:
    bit = b & 1
    if bit:
        result = result * a % m
    print(f"{a:>6} {b:>4} {bit:>4} {result:>7}")
    a = a * a % m
    b >>= 1
print("answer:", result, "check:", 3 ** 13 % 1000)
```
```text
  base  exp  bit  result
     3   13    1       3
     9    6    0       3
    81    3    1     243
   561    1    1     323
answer: 323 check: 323
```

Each line shows the base *before* squaring and the result *after* using the bit. Read the bits of `13 = 1101` from the
lowest: `1, 0, 1, 1`. The rows with `bit = 1` multiply the current base into the result; the row with `bit = 0` only squares.

### The built-in `pow(a, b, m)`

Python does all of this for you, in C, faster than any loop you can write:

```python
print(pow(2, 10, 1000))
print(pow(7, 10**18, 10**9 + 7))
print(pow(2, 5, 1))
```
```text
24
259616729
0
```

You should write the loop by hand once (so you can explain it, and so you can use it in problems that forbid or
replace `pow`), and use `pow(a, b, m)` from then on. The same loop works for other "multiplications": for example
matrix powers (Fibonacci in O(log n)) and string repetition. Whenever "combine `b` copies of something associative"
appears, think binary exponentiation.

### Huge exponents

Sometimes the exponent `b` is itself a huge number given as a decimal string with 100,000 digits. Python can read it with
`int(text)` (after raising the digit limit; judges for such problems usually allow it, or you can process digit by
digit). Then `pow(a, b, m)` still takes only `O(log b)` multiplications, i.e. about 330,000 squarings for 100,000 digits. If
`m` is prime and `gcd(a, m) = 1` you may first reduce `b` modulo `m - 1` (Fermat), which can be done digit by digit.

```python
def mod_of_decimal_string(digits, m):
    r = 0
    for ch in digits:
        r = (r * 10 + int(ch)) % m
    return r

big = "9" * 50
p = 10**9 + 7
print(mod_of_decimal_string(big, p - 1) == int(big) % (p - 1))
print(pow(3, mod_of_decimal_string(big, p - 1), p) == pow(3, int(big), p))
```
```text
True
True
```

This reads a decimal number one digit at a time, the same way you read digits in school, and never needs the number as a
whole. That is exactly why "given as a string" problems are solvable even in languages without big integers.

**Try it 11: modular rules**

Predict `(10**20 + 10**20 + 5) % 7`. Which of these is wrong and why? (a) `(a + b) % m`, (b) `(a % m + b % m) % m`,
(c) `(a % m + b % m)` printed without the final `% m`.

<details><summary>Answer</summary>

```python
m = 7
a = b = 10**20
print((a + b + 5) % m)
print((a % m + b % m + 5) % m)
print(a % m + b % m + 5)
```
```text
2
2
9
```

(a) and (b) agree and are right. (c) is wrong as an answer: the sum of two residues may be as large as `2m - 2`,
so the final reduction is essential. Every `+` and every `*` can push you out of `0 .. m-1`.
</details>

**Try it 12: trace fast exponentiation**

By hand, compute `2 ** 11 mod 1000` with the loop above. Write `(a, b, result)` for each iteration. Then check by running.

<details><summary>Answer</summary>

```python
a, b, m, result = 2, 11, 1000, 1
while b > 0:
    if b & 1:
        result = result * a % m
    print(a, b, result)
    a = a * a % m
    b >>= 1
print(result == 2 ** 11 % 1000)
```
```text
2 11 2
4 5 8
16 2 8
256 1 48
True
```

`11 = 1011` in binary: 1, 1, 0, 1 from the lowest bit. The result picks up `2`, then `4`, skips `16`, then picks up `256`:
`2 * 4 * 256 = 2048`, and `2048 mod 1000 = 48`.
</details>

## 8. Modular inverses and division

### Definition

The **modular inverse** of `a` modulo `m` is a number `x` with `a * x == 1 (mod m)`. We write `x = a^{-1}`. With it, "divide by `a`"
means "multiply by `x`": `b / a  ==  b * x (mod m)`. Why that is the right meaning: if `b = a * c` exactly, then
`b * x = a * c * x == c * (a * x) == c * 1 = c`. We recover the true quotient `c`, but modulo `m`.

### When does it exist?

The inverse of `a` exists **if and only if `gcd(a, m) = 1`**.

- *If* `gcd = 1`: extended Euclid gives `a x + m y = 1`, and then `a x == 1 (mod m)`.
- *Only if*: if `a x == 1 (mod m)`, then `a x - 1 = m y`, so any common divisor of `a` and `m` divides `1`. So the gcd is `1`.

Examples: `3` has an inverse modulo `7` (it is `5`, since `15 = 2*7 + 1`). `4` has **no** inverse modulo `10` (they share the
factor `2`: the products `4*k mod 10` are only `0, 4, 8, 2, 6`, never `1`).

When `m` is **prime**, every `a` not divisible by `m` has an inverse. That is exactly why `10^9 + 7` is chosen.

```python
m = 7
for a in range(1, m):
    inv = next(x for x in range(1, m) if a * x % m == 1)
    print(f"inverse of {a} mod {m} is {inv}")
m = 10
print([a for a in range(1, m) if any(a * x % m == 1 for x in range(1, m))])
```
```text
inverse of 1 mod 7 is 1
inverse of 2 mod 7 is 4
inverse of 3 mod 7 is 5
inverse of 4 mod 7 is 2
inverse of 5 mod 7 is 3
inverse of 6 mod 7 is 6
[1, 3, 7, 9]
```

Modulo 10 only `1, 3, 7, 9` have inverses: those coprime to 10.

### Method 1: Fermat's little theorem (prime modulus)

**Fermat's little theorem:** if `p` is prime and `p` does not divide `a`, then `a^(p-1) == 1 (mod p)`.

**Why (sketch).** Multiply each of `1, 2, ..., p-1` by `a` modulo `p`. Because `a` has an inverse, the results are all different, so they are
a rearrangement of `1, ..., p-1`. Multiplying all the numbers on each side: `a^(p-1) * (p-1)! == (p-1)! (mod p)`.
Since `(p-1)!` is coprime to `p`, we may cancel it.

So `a * a^(p-2) == 1`, and therefore:

```text
inverse of a mod p = a ** (p - 2) % p
```

```python
p = 10**9 + 7

def inv_fermat(a, p):
    return pow(a, p - 2, p)

print(inv_fermat(3, 7), inv_fermat(2, p), inv_fermat(2, p) * 2 % p)
print(all(a * inv_fermat(a, 101) % 101 == 1 for a in range(1, 101)))
```
```text
5 500000004 1
True
```

Cost: one fast exponentiation, about `30` squarings for `p ~ 10^9`. Works **only** when `p` is prime.

### Method 2: extended Euclid (any modulus, if coprime)

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def inv_mod(a, m):
    g, x, _ = ext_gcd(a % m, m)
    if g != 1:
        return None          # no inverse
    return x % m

print(inv_mod(3, 7), inv_mod(4, 10), inv_mod(3, 10), inv_mod(7, 10**18 + 9))
print(inv_mod(10**9 + 6, 10**9 + 7))
```
```text
5 None 7 285714285714285717
1000000006
```

This works for any modulus `m` (prime or not), including modulus values around `10^18`, and tells you honestly when no inverse exists.

### Method 3: `pow(a, -1, m)`

Since Python 3.8 the built-in `pow` does the extended Euclid for you when the exponent is `-1`:

```python
print(pow(3, -1, 7), pow(7, -1, 10**18 + 9))
try:
    print(pow(4, -1, 10))
except ValueError as error:
    print("ValueError:", error)
```
```text
5 285714285714285717
ValueError: base is not invertible for the given modulus
```

That is the shortest and the best choice once you understand it. It raises `ValueError` when no inverse exists.

### Inverses of 1 .. n in linear time

If you need `inv[1], inv[2], ..., inv[n]` modulo a prime `p`, calling `pow` `n` times costs `O(n log p)`. There is a neat linear recurrence:

```text
inv[1] = 1
inv[i] = (p - (p // i) * inv[p % i] % p) % p
```

Why: write `p = (p // i) * i + p % i`. Taking this mod `p`: `0 == (p // i) * i + (p % i)`, so `i == -(p % i) / (p // i)`, so `1 / i == -(p // i) * inv(p % i)`. 

```python
p = 1_000_000_007
n = 20
inv = [0, 1] + [0] * (n - 1)
for i in range(2, n + 1):
    inv[i] = (p - (p // i) * inv[p % i] % p) % p
print(inv[1:8])
print(all(inv[i] == pow(i, p - 2, p) for i in range(1, n + 1)))
```
```text
[1, 500000004, 333333336, 250000002, 400000003, 166666668, 142857144]
True
```

It works because `p % i < i`, so `inv[p % i]` is already computed.

### Fermat or extended Euclid?

| | Fermat `a ** (m-2)` | Extended Euclid / `pow(a, -1, m)` |
|---|---|---|
| Modulus must be prime? | **Yes** | No, just `gcd(a, m) = 1` |
| Detects "no inverse"? | No (silently returns garbage) | Yes (`None` / `ValueError`) |
| Speed | `log m` multiplications | `log m` divisions |
| Typical use | contests with `10^9 + 7` | any modulus, CRT, congruences |

**Try it 13: inverse by hand**

Find the inverse of `5` modulo `13` by trying values, then by Fermat's formula `5 ** 11 % 13`. Does `6` have an inverse modulo `9`?

<details><summary>Answer</summary>

```python
print(next(x for x in range(1, 13) if 5 * x % 13 == 1), pow(5, 11, 13))
print(any(6 * x % 9 == 1 for x in range(9)))
```
```text
8 8
False
```

`5 * 8 = 40 = 3*13 + 1`, so the inverse is `8`. For `6` modulo `9`, `gcd(6, 9) = 3 != 1`, so there is no inverse.
</details>

**Try it 14: divide under a modulus**

Compute `(1000 // 8) % 13` the exact way. Then compute `1000 * inverse(8) % 13`. Why do they agree? Then try `(1001 // 8) % 13`
and `1001 * inverse(8) % 13` and explain why they may not.

<details><summary>Answer</summary>

```python
inv8 = pow(8, -1, 13)
print(1000 // 8 % 13, 1000 * inv8 % 13)
print(1001 // 8 % 13, 1001 * inv8 % 13)
```
```text
8 8
8 0
```

`1000` is exactly divisible by `8`, so the modular division recovers the true quotient `125`. `1001` is not divisible by `8`, so `//` rounds down and
the "true quotient" is not an integer at all. The inverse formula is only meaningful as division when the exact quotient exists.
</details>

## 9. Counting: nCr, Pascal's triangle, Legendre and Euler

### nCr

`C(n, r)` ("n choose r") is the number of ways to pick `r` items from `n` when order does not matter. The formula:

```text
C(n, r) = n! / (r! * (n - r)!)
```

Think: `n!` arranges all `n` items; but the order inside the chosen group (`r!` ways) and inside the unchosen group
(`(n - r)!` ways) is irrelevant, so divide those out. Properties: `C(n, 0) = C(n, n) = 1`, `C(n, r) = C(n, n - r)`, and `C(n, r) = 0` when `r > n`.

### Method 1: Pascal's triangle

**The rule:** `C(n, r) = C(n - 1, r - 1) + C(n - 1, r)`. Why: pick one special item. Either it is in the group (then choose the remaining
`r - 1` from the other `n - 1`) or it is not (choose `r` from the other `n - 1`).

```python
def pascal_rows(n):
    row = [1]
    rows = [row]
    for _ in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
        rows.append(row)
    return rows

for row in pascal_rows(7):
    print(*row)
print(pascal_rows(60)[60][30])
```
```text
1
1 1
1 2 1
1 3 3 1
1 4 6 4 1
1 5 10 10 5 1
1 6 15 20 15 6 1
1 7 21 35 35 21 7 1
118264581564861424
```

Each row costs `O(n)` and we need `n` rows: `O(n^2)` time (and `O(n)` memory if we keep only the last row). All values are exact. This is
simple, never divides, and is perfect when `n` is a few thousand at most, for example `n <= 5000` with many queries (one `5000 x 5000` table is 25 million
entries, which is the limit). For `n = 60` with exact answers this is all you need.

You can also use the reduction modulo `m` in the table, `(a + b) % m`, with no problem: addition survives the modulus.

### Method 2: factorials and inverse factorials (n up to ~10^6 or 10^7)

When `n` is large but you ask many queries, precompute once:

- `fact[i] = i! mod p` for `i = 0..N`.
- `inv_fact[i] = (i!)^{-1} mod p`. Compute **only one** inverse, `inv_fact[N] = pow(fact[N], p - 2, p)`, then go downward:
  `inv_fact[i - 1] = inv_fact[i] * i % p`. Why: `1/(i-1)! = i / i!`.

Then every query is three multiplications: `C(n, r) = fact[n] * inv_fact[r] % p * inv_fact[n - r] % p`.

```python
MOD = 10**9 + 7
N = 1000

fact = [1] * (N + 1)
for i in range(1, N + 1):
    fact[i] = fact[i - 1] * i % MOD

inv_fact = [1] * (N + 1)
inv_fact[N] = pow(fact[N], MOD - 2, MOD)
for i in range(N, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD

def ncr(n, r):
    if r < 0 or r > n:
        return 0
    return fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD

import math
print(ncr(10, 3), ncr(1000, 500), ncr(5, 7), ncr(7, 0))
print(ncr(1000, 500) == math.comb(1000, 500) % MOD)
print(all(fact[i] * inv_fact[i] % MOD == 1 for i in range(N + 1)))
```
```text
120 159835829 0 1
True
True
```

Setup is `O(N)` plus one `pow`; each query is `O(1)`. This is the main tool for "answer `10^5` queries of `C(n, r) mod 10^9 + 7`".

**Requirements.** `N` must be smaller than the modulus `p` (so that no factorial is divisible by `p`, which would make it non-invertible),
and `p` must be prime (or at least coprime to every number up to `N`). For `n >= p` you need Lucas's theorem; outside this chapter.

### Which method when?

| Situation | Method |
|---|---|
| Small `n` (<= ~60), exact value wanted | Pascal row or `math.comb` |
| `n <= ~5000`, many queries, any modulus (even non-prime) | Pascal table, only additions |
| `n` up to `10^6..10^7`, prime modulus, many queries | factorial + inverse factorial |
| One huge `n` with a small `r` | multiply `r` terms and divide by `r!` using an inverse |
| Modulus not prime, large `n` | factor the modulus, work per prime power (advanced) |

### The classic bug: dividing under a modulus

```python
MOD = 10**9 + 7
from math import factorial

def ncr_wrong(n, r):
    return factorial(n) % MOD // (factorial(r) % MOD * (factorial(n - r) % MOD)) % MOD

def ncr_right(n, r):
    from math import comb
    return comb(n, r) % MOD

print(ncr_wrong(10, 3), ncr_right(10, 3))
print(ncr_wrong(40, 20), ncr_right(40, 20))
```
```text
120 120
0 846527861
```

For tiny `n` the wrong version happens to match because `n!` is below the modulus; once `n!` exceeds `p`, `fact % p` is a remainder, and a remainder cannot
be divided with `//`. Always multiply by inverses. The same applies to `(a + b) % m // 2`: that is not "half of the answer".

### Legendre's formula: the exponent of a prime in n!

How many trailing zeros does `100!` have? A trailing zero is a factor `10 = 2 * 5`. There are far more 2s than 5s, so we count 5s.
Among `1..n`: `n // 5` numbers are multiples of 5, `n // 25` of those have a second 5, `n // 125` a third, and so on:

```text
v_p(n!) = n // p + n // p**2 + n // p**3 + ...
```

```python
def legendre(n, p):
    total = 0
    power = p
    while power <= n:
        total += n // power
        power *= p
    return total

print(legendre(100, 5), legendre(100, 2), legendre(25, 5), legendre(24, 5))
print(legendre(10**18, 5))

import math
f = math.factorial(100)
zeros = 0
while f % 10 == 0:
    f //= 10
    zeros += 1
print(zeros)
```
```text
24 97 6 4
249999999999999995
24
```

It takes `log_p(n)` steps even when `n = 10^18`. A helpful alternative form: `v_p(n!) = (n - digit_sum_base_p(n)) / (p - 1)`.

It also gives the exponent of `p` in `C(n, r)`: `v_p(n!) - v_p(r!) - v_p((n - r)!)`. For example `C(10, 5) = 252 = 4 * 63` has `2^2` in it, and
`legendre(10, 2) - 2 * legendre(5, 2) = 8 - 2 * 3 = 2`. If the exponent is positive, `p` divides `C(n, r)`.

### Euler's totient function

`phi(n)` is the count of numbers in `1 .. n` that are **coprime** to `n`. `phi(1) = 1`, `phi(p) = p - 1` for prime `p`, `phi(p^k) = p^k - p^(k-1)`
(only multiples of `p` are excluded: that is `p^(k-1)` of them). And `phi` is **multiplicative**: if `gcd(a, b) = 1` then `phi(a b) = phi(a) phi(b)`.
Putting it together, from the prime factorisation:

```text
phi(n) = n * (1 - 1/p1) * (1 - 1/p2) * ... * (1 - 1/pk)      (p1..pk are the distinct primes of n)
```

In code: start with `result = n`; for each distinct prime factor `p`, do `result -= result // p`. This avoids fractions, and the division is exact.

```python
def phi(n):
    result = n
    d = 2
    while d * d <= n:
        if n % d == 0:
            while n % d == 0:
                n //= d
            result -= result // d
        d += 1
    if n > 1:
        result -= result // n
    return result

print([phi(n) for n in range(1, 21)])
print(phi(36), phi(97), phi(10**12))

import math
print([phi(n) for n in range(1, 40)] == [sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1) for n in range(1, 40)])
```
```text
[1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18, 8]
12 96 400000000000
True
```

For many queries, adapt the sieve: start with `phi[i] = i`; for each prime `p`, for every multiple `m` do `phi[m] -= phi[m] // p`:

```python
n = 30
phi = list(range(n + 1))
for p in range(2, n + 1):
    if phi[p] == p:                         # untouched so far: p is prime
        for m in range(p, n + 1, p):
            phi[m] -= phi[m] // p
print(phi[1:])
```
```text
[1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16, 6, 18, 8, 12, 10, 22, 8, 20, 12, 18, 12, 28, 8]
```

**Euler's theorem.** If `gcd(a, m) = 1` then `a ** phi(m) == 1 (mod m)`. It generalises Fermat (`phi(p) = p - 1`) and gives the
inverse `a ** (phi(m) - 1)` for any modulus when `gcd(a, m) = 1`. It is also why exponents can be reduced modulo `phi(m)` (for coprime `a`).

A related formula that shows up: `gcd(1, n) + gcd(2, n) + ... + gcd(n, n) = sum over divisors d of n of d * phi(n / d)`.
Group the `k` by `g = gcd(k, n) = d`: there are `phi(n / d)` of them.

```python
import math

def phi(n):
    result = n
    d = 2
    while d * d <= n:
        if n % d == 0:
            while n % d == 0:
                n //= d
            result -= result // d
        d += 1
    if n > 1:
        result -= result // n
    return result

def gcd_sum_formula(n):
    return sum(d * phi(n // d) for d in range(1, n + 1) if n % d == 0)

def gcd_sum_slow(n):
    return sum(math.gcd(k, n) for k in range(1, n + 1))

print([gcd_sum_formula(n) for n in range(1, 13)])
print([gcd_sum_slow(n) for n in range(1, 13)])
```
```text
[1, 3, 5, 8, 9, 15, 13, 20, 21, 27, 21, 40]
[1, 3, 5, 8, 9, 15, 13, 20, 21, 27, 21, 40]
```

**Try it 15: Pascal by hand**

Write rows 0 to 5 of Pascal's triangle by hand. Which entries of row 5 are even? What is `C(5, 2)` using the factorial formula?

<details><summary>Answer</summary>

```python
import math
for n in range(6):
    print([math.comb(n, r) for r in range(n + 1)])
print(math.factorial(5) // (math.factorial(2) * math.factorial(3)))
```
```text
[1]
[1, 1]
[1, 2, 1]
[1, 3, 3, 1]
[1, 4, 6, 4, 1]
[1, 5, 10, 10, 5, 1]
10
```

Row 5 is `1 5 10 10 5 1`; the even entries are the two `10`s. And `5! / (2! 3!) = 120 / 12 = 10`.
</details>

**Try it 16: trailing zeros**

How many trailing zeros does `1000!` have? Do it with Legendre by hand: `1000 // 5 + 1000 // 25 + 1000 // 125 + 1000 // 625`.

<details><summary>Answer</summary>

```python
print(1000 // 5 + 1000 // 25 + 1000 // 125 + 1000 // 625)
import math
s = str(math.factorial(1000))
print(len(s) - len(s.rstrip("0")))
```
```text
249
249
```

`200 + 40 + 8 + 1 = 249`. The brute-force count on the exact factorial confirms it.
</details>

**Try it 17: phi by hand**

Compute `phi(36)`, `phi(100)`, `phi(97)`. Use `n * (1 - 1/p)` for each distinct prime `p`.

<details><summary>Answer</summary>

```python
def phi(n):
    result, d = n, 2
    while d * d <= n:
        if n % d == 0:
            while n % d == 0:
                n //= d
            result -= result // d
        d += 1
    if n > 1:
        result -= result // n
    return result

print(phi(36), phi(100), phi(97))
```
```text
12 40 96
```

`36 = 2^2 * 3^2`, so `36 * (1/2) * (2/3) = 12`. `100 = 2^2 * 5^2`, so `100 * (1/2) * (4/5) = 40`. `97` is prime, so `96`.
</details>

**Try it 18: when does the factorial method break?**

Suppose the modulus is `p = 13` and you precompute `fact` up to `N = 20`. What goes wrong with `inv_fact[20]`? Test `pow(fact[20], 11, 13)`.

<details><summary>Answer</summary>

```python
p = 13
fact = 1
for i in range(1, 21):
    fact = fact * i % p
print(fact)
print(pow(fact, p - 2, p))
```
```text
0
0
```

`20!` contains the factor `13`, so `20! mod 13 = 0`, and `0` has no inverse; Fermat then returns `0`, which is wrong. The precomputation is valid only for `N < p`.
</details>


## 10. Bit manipulation

### Why bits

A computer stores integers in binary, as a row of bits (0 or 1). A number's bits are a tiny, very fast array of yes/no
flags. Two kinds of problems use this directly:

- **Speed and memory tricks**: testing "is it a power of two?", counting how many bits are set, swapping without a temporary.
- **Subsets**: a set of up to ~20 items can be stored as one integer, where bit `i` says "item `i` is in the set". Then looping over
  `0 .. 2**n - 1` visits **every subset** exactly once.

### Binary refresher

`13` in binary is `1101`, meaning `8 + 4 + 0 + 1`. Bit positions are counted from the right, starting at 0: bit 0 is the
lowest (value 1), bit 3 has value 8.

```python
for n in [0, 1, 5, 13, 255, 256]:
    print(n, bin(n), format(n, "08b"), int(bin(n), 2))
print(int("1101", 2), int("ff", 16), hex(255), (13).bit_length())
```
```text
0 0b0 00000000 0
1 0b1 00000001 1
5 0b101 00000101 5
13 0b1101 00001101 13
255 0b11111111 11111111 255
256 0b100000000 100000000 256
13 255 0xff 4
```

`bin(n)` gives a string with prefix `0b`. `format(n, "08b")` pads to 8 binary digits. `int(text, 2)` parses binary. `n.bit_length()`
is the number of bits needed (0 for 0).

### The operators

| Operator | Name | Rule (bit by bit) |
|---|---|---|
| `a & b` | AND | 1 only if both bits are 1 |
| `a \| b` | OR | 1 if either bit is 1 |
| `a ^ b` | XOR | 1 if the bits differ |
| `~a` | NOT | flip every bit (see below: equals `-a - 1`) |
| `a << k` | left shift | move bits left by `k`, fill zeros: `a * 2**k` |
| `a >> k` | right shift | move bits right by `k`: `a // 2**k` (floor) |

```python
a, b = 12, 10          # 1100 and 1010
print(format(a, "04b"), format(b, "04b"))
print(format(a & b, "04b"), a & b)
print(format(a | b, "04b"), a | b)
print(format(a ^ b, "04b"), a ^ b)
print(1 << 4, 5 << 2, 100 >> 3, 100 // 8)
```
```text
1100 1010
1000 8
1110 14
0110 6
16 20 12 12
```

### The everyday bit idioms

With `1 << i` being the number that has only bit `i` set (a **mask**):

| Task | Code |
|---|---|
| Test bit `i` | `(n >> i) & 1` or `n & (1 << i)` |
| Set bit `i` | `n \| (1 << i)` |
| Clear bit `i` | `n & ~(1 << i)` |
| Toggle bit `i` | `n ^ (1 << i)` |
| Is `n` odd? | `n & 1` |
| Multiply / divide by `2**k` | `n << k` / `n >> k` |
| Keep the lowest `k` bits (`n % 2**k`) | `n & ((1 << k) - 1)` |

```python
n = 0b101100          # 44
print(bin(n))
print("bit 2 set?", (n >> 2) & 1, " bit 1 set?", (n >> 1) & 1)
print("set bit 0:", bin(n | (1 << 0)))
print("clear bit 3:", bin(n & ~(1 << 3)))
print("toggle bit 5:", bin(n ^ (1 << 5)))
print("low 4 bits:", bin(n & ((1 << 4) - 1)), "==", n % 16)
```
```text
0b101100
bit 2 set? 1  bit 1 set? 0
set bit 0: 0b101101
clear bit 3: 0b100100
toggle bit 5: 0b1100
low 4 bits: 0b1100 == 12
```

Operator precedence is a classic trap. In C and C++, `n & 1 == 0` means `n & (1 == 0)`, which is a bug. In Python the
comparison operators bind more loosely than `&`, `|` and `^`, so the same text happens to work. Check it:

```python
n = 6
print(n & 1 == 0)
print((n & 1) == 0)
print(n & (1 == 0))
```
```text
True
True
0
```

The first two lines agree and the third differs. Still, **always parenthesise** a bit operation inside a larger expression,
`(n & 1) == 0`, so that the code is correct in any language and obvious to the reader. Another precedence trap: `+` and `-`
bind *tighter* than shifts, so `1 << n + 1` is `1 << (n + 1)`, not `(1 << n) + 1`.

### n & (n - 1): clear the lowest set bit

Subtract 1 from `n`: the lowest `1` bit becomes `0` and every `0` bit below it becomes `1`. All bits above are unchanged.
ANDing with `n` therefore zeroes exactly that lowest set bit and everything below it (which was already 0).

```text
n      = 1 0 1 1 0 0      (44)
n - 1  = 1 0 1 0 1 1      (43)
n&(n-1)= 1 0 1 0 0 0      (40)  lowest set bit removed
```

Uses:

- **Count set bits** (popcount): repeat `n &= n - 1` until `n == 0`; the number of repetitions is the answer. It takes as
  many steps as there are set bits, not 32 or 64.
- **Power of two test**: a power of two has exactly one set bit, so `n > 0 and n & (n - 1) == 0`.

```python
def popcount(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

print([popcount(n) for n in [0, 1, 7, 8, 255, 256, 1023]])
print([n for n in range(1, 40) if is_power_of_two(n)])
print(popcount(2**100 - 1), bin(2**100 - 1).count("1"))
```
```text
[0, 1, 3, 1, 8, 1, 10]
[1, 2, 4, 8, 16, 32]
100 100
```

`bin(n).count("1")` is the simplest popcount; and newer Python versions (3.10 and later) also have `n.bit_count()`. Hand-writing the loop
shows why it is efficient, and it is what the problems expect first.

### n & -n: isolate the lowest set bit

What does `-n` look like in binary? On a computer, negative numbers use **two's complement**: `-n` is "flip all bits of `n`, then add 1".
Flipping turns the lowest 1 into 0 and the zeros below it into 1s; adding 1 carries through those 1s, turns them back to 0 and sets the
lowest-1 position to 1 again. Everything above is flipped, so it differs from `n`. Thus `n & -n` keeps **only** the lowest set bit.

```python
for n in [12, 40, 7, 64, 1]:
    print(f"n={n:>3} {n:>8b}   -n&n -> {n & -n:>3} {n & -n:>8b}")
```
```text
n= 12     1100   -n&n ->   4      100
n= 40   101000   -n&n ->   8     1000
n=  7      111   -n&n ->   1        1
n= 64  1000000   -n&n ->  64  1000000
n=  1        1   -n&n ->   1        1
```

Uses: the value of the lowest set bit; the index of the lowest set bit is `(n & -n).bit_length() - 1`; and Fenwick trees (a later module)
rely on `i += i & -i`.

### Python's negative numbers and `~`

Python integers behave as if they had an **infinite** number of bits, with negative numbers using an endless string of leading 1s (two's
complement without a width). That is why:

```text
~n  ==  -n - 1
```

Flipping every bit of an infinite-length number turns `n` into `-(n + 1)`. And `bin(-5)` prints `-0b101`: Python shows the sign
separately, not the infinite 1s.

```python
for n in [0, 1, 5, -1, -5]:
    print(n, ~n, -n - 1)
print(bin(5), bin(-5), bin(~5))
print(-5 & 0xFF, bin(-5 & 0xFF))
print(-1 >> 3, -8 >> 1, -7 >> 1, -7 // 2)
```
```text
0 -1 -1
1 -2 -2
5 -6 -6
-1 0 0
-5 4 4
0b101 -0b101 -0b110
251 0b11111011
-1 -4 -4 -4
```

- `-5 & 0xFF` gives `251`: masking with a width of 8 bits *simulates* an 8-bit two's complement value `11111011`. To get a fixed-width
  view of a negative number, AND it with `(1 << width) - 1`.
- A right shift of a negative number **rounds down** (the same as `//`): `-7 >> 1 = -4`, and `-1 >> 3 = -1` (stays -1 forever).
- Left shift never overflows: `1 << 100` is just a big integer. In C++ it would be undefined or wrap around. In Python, if a problem says
  "treat it as a 32-bit unsigned integer" you must mask yourself: `(x << 5) & 0xFFFFFFFF`.

```python
MASK32 = 0xFFFFFFFF
x = 0xDEADBEEF
print((x << 8) & MASK32, hex((x << 8) & MASK32))
print((x << 8))
```
```text
2914971392 0xadbeef00
956397711104
```

The first result is what a C program with `unsigned int` would print; the second is the true Python value, with 8 extra bits at the top.

**Try it 19: predict the output (bits)**

Decide on each line before checking.

```python
print(6 & 3, 6 | 3, 6 ^ 3)
print(1 << 10, 1000 >> 2)
print(~0, ~7, ~-1)
print(12 & -12)
print(-9 >> 1, -9 & 7)
print(5 ^ 5, 5 ^ 0, 5 ^ 1)
```

<details><summary>Answer</summary>

```text
2 7 5
1024 250
-1 -8 0
4
-5 7
0 5 4
```

`6 = 110`, `3 = 011`: AND `010 = 2`, OR `111 = 7`, XOR `101 = 5`. `~0 = -1`, `~7 = -8`, `~-1 = 0`. `12 & -12 = 4`, the lowest set bit of 12 (`1100`).
`-9 >> 1 = -5` (floor of `-4.5`), and `-9 & 7 = 7` because `-9 = ...11110111` and the lowest three bits are `111`.
The last line: `x ^ x = 0`, `x ^ 0 = x`, `5 ^ 1 = 4` (bit 0 flipped).
</details>

### Subsets with bitmasks

A set of `n` items, numbered `0 .. n-1`, is stored as an integer `mask`: item `i` is in the set exactly when bit `i` of `mask` is 1.
All `2**n` subsets are the numbers `0 .. 2**n - 1`. `mask = 0` is the empty set and `mask = 2**n - 1` is the full set.

```python
items = ["a", "b", "c"]
n = len(items)
for mask in range(1 << n):
    chosen = [items[i] for i in range(n) if (mask >> i) & 1]
    print(f"{mask:03b}", chosen)
```
```text
000 []
001 ['a']
010 ['b']
011 ['a', 'b']
100 ['c']
101 ['a', 'c']
110 ['b', 'c']
111 ['a', 'b', 'c']
```

This is the standard way to try **every subset** when `n <= 20` (about a million masks; `n = 18` is `262,144` masks, each needing up to 18 bit tests).
For example, count the subsets of a list that sum to a target:

```python
def count_subsets_with_sum(values, target):
    n = len(values)
    count = 0
    for mask in range(1 << n):
        total = 0
        for i in range(n):
            if (mask >> i) & 1:
                total += values[i]
        if total == target:
            count += 1
    return count

print(count_subsets_with_sum([1, 2, 3, 4, 5], 5))
print(count_subsets_with_sum([1, 1, 1, 1], 2))
print(count_subsets_with_sum([3, 5], 0))
```
```text
3
6
1
```

The empty subset is counted when `target = 0`: it sums to `0`. Notice the last line: `[3, 5]` has one subset (the empty one) with sum `0`.
Always think about whether the empty set counts in the problem you are solving.

Subset operations map to bit operations: union is `a | b`, intersection `a & b`, "in `a` but not `b`" is `a & ~b`,
complement within `n` items is `full ^ a` (where `full = (1 << n) - 1`), and "is `a` a subset of `b`?" is `a & b == a`.
To enumerate the **submasks** of a mask: `sub = mask; while sub: ...; sub = (sub - 1) & mask`.

```python
mask = 0b1011
subs = []
sub = mask
while sub:
    subs.append(format(sub, "04b"))
    sub = (sub - 1) & mask
subs.append("0000")
print(subs)
```
```text
['1011', '1010', '1001', '1000', '0011', '0010', '0001', '0000']
```

### XOR and its three laws

XOR has three properties that solve a whole family of problems:

1. `x ^ 0 = x`.
2. `x ^ x = 0`.
3. It is commutative and associative: the order does not matter.

**Single number.** In a list where every value appears exactly twice except one, XOR of **all** values is that one: each pair cancels
(`x ^ x = 0`), zeros disappear, and what remains is the lone value. O(n) time and O(1) memory, no dictionary needed.

```python
def single_number(values):
    result = 0
    for v in values:
        result ^= v
    return result

print(single_number([4, 1, 2, 1, 2]))
print(single_number([7]))
print(single_number([10**18, 5, 5, 10**18, 99]))
```
```text
4
7
99
```

**Swapping without a temporary**: `a ^= b; b ^= a; a ^= b`. After the first step `a = a ^ b`; then `b = b ^ (a ^ b) = a_old`; then
`a = (a ^ b_old) ^ a_old = b_old`. In Python you simply write `a, b = b, a`, so this trick is only for understanding XOR. (And it fails when
both names are the *same location*, such as swapping `x[i]` with `x[i]` by index, where it zeroes the value.)

```python
a, b = 12, 5
a ^= b
b ^= a
a ^= b
print(a, b)
x = [9, 8]
i = j = 0
x[i] ^= x[j]; x[j] ^= x[i]; x[i] ^= x[j]
print(x)
```
```text
5 12
[0, 8]
```

**Two single numbers.** Suppose *two* values `u` and `v` appear once and all others twice. XOR of everything is `u ^ v`, and
since `u != v` it is non-zero, so at least one bit is `1`, which means `u` and `v` differ at that bit. Take the lowest set
bit `low = x & -x` of the XOR. Split the numbers into two groups by whether they have that bit. `u` and `v` land in different groups, and each pair of equal
numbers lands in the same group. XOR each group: you get `u` and `v`.

```python
def two_singles(values):
    x = 0
    for v in values:
        x ^= v
    low = x & -x
    u = v2 = 0
    for v in values:
        if v & low:
            u ^= v
        else:
            v2 ^= v
    return min(u, v2), max(u, v2)

print(two_singles([1, 2, 1, 3, 2, 5]))
print(two_singles([0, 6, 6, 9]))
```
```text
(3, 5)
(0, 9)
```

**Missing number.** For `0 .. n` with one value missing, XOR all numbers `0 .. n` together with all list values; every number present cancels and the
missing one is left.

```python
def missing(values):
    n = len(values)
    result = n
    for i, v in enumerate(values):
        result ^= i ^ v
    return result

print(missing([3, 0, 1]), missing([0, 1]), missing([9, 6, 4, 2, 3, 5, 7, 0, 1]))
```
```text
2 2 8
```

### Handy facts

- `n.bit_length()` gives the number of bits; `2 ** (bit_length - 1) <= n < 2 ** bit_length` for `n > 0`. So `floor(log2(n)) = n.bit_length() - 1`, exactly, with no floats.
- The next power of two `>= n` (for `n >= 1`): `1 << (n - 1).bit_length()`.
- Parity of popcount, Gray code `n ^ (n >> 1)`, and "which bits differ between `a` and `b`": `a ^ b`; the Hamming distance is `popcount(a ^ b)`.
- Bits are the right tool when the problem says "subsets of at most 20 items" or "all numbers appear twice". They are the wrong tool when readability suffers for no gain; `n % 2 == 0` is fine.

**Try it 20: popcount trace**

Trace `n &= n - 1` on `n = 0b101101` (45). Write `n` in binary after each step and count the steps.

<details><summary>Answer</summary>

```python
n = 45
steps = 0
print(format(n, "06b"))
while n:
    n &= n - 1
    steps += 1
    print(format(n, "06b"))
print("steps:", steps)
```
```text
101101
101100
101000
100000
000000
steps: 4
```

Each step removes the lowest set bit; 45 has 4 set bits so there are 4 steps.
</details>

**Try it 21: single number by XOR**

Without running, compute `3 ^ 5 ^ 3 ^ 7 ^ 5`. Then write a version that fails when the values include a number appearing **three** times,
and explain why XOR cannot solve that case directly.

<details><summary>Answer</summary>

```python
print(3 ^ 5 ^ 3 ^ 7 ^ 5)
print(2 ^ 2 ^ 2)
```
```text
7
2
```

The pairs of 3 and 5 cancel and `7` remains. If a value appears three times, XOR keeps it (`x ^ x ^ x = x`). XOR only cancels **even** counts;
three copies cancel two and leave one. For "all appear three times except one" one counts the bits modulo 3 instead.
</details>

## 11. Common traps

A checklist to read before you submit any number-theory solution.

1. **Using `/` instead of `//`.** `/` returns a float with 53 bits of precision, so for values above `2**53` the answer is rounded. `10**18 // 7` is exact; `10**18 / 7` is not.
2. **`int(n ** 0.5)` for the square root.** It can be off by one for large `n`. Use `math.isqrt(n)` or the loop condition `d * d <= n`.
3. **Forgetting `1` is not prime**, `0` is not prime, `2` is the only even prime. Test `n = 0, 1, 2, 3, 4` in any primality code.
4. **Sieve boundaries**: allocate `n + 1` entries; start crossing at `p * p`; mark `0` and `1` as not prime.
5. **Reusing the shrinking `n`** in factorisation: after dividing out factors, `n` changed. Save `original = n` if you still need it.
6. **A leftover prime**: after the trial loop, `n > 1` means one last prime factor remains. Forgetting it gives `n = 14` as `(2, 1)` only.
7. **Taking `lcm` of residues.** The LCM must be computed from exact numbers (or by prime powers). `lcm(a % m, b % m) % m` is wrong.
8. **`gcd(a, 0)`**: it is `a`, not an error. And `lcm(a, 0) = 0`.
9. **Missing the final `% m`.** After a sum or product the value can leave `0 .. m-1`. Reduce at every step of a running total.
10. **Dividing under a modulus** with `//` or `/`. Multiply by the modular inverse instead.
11. **Fermat with a composite modulus.** `a ** (m - 2) % m` is the inverse only for prime `m`. Use extended Euclid (`pow(a, -1, m)`) for any other modulus.
12. **No inverse exists** when `gcd(a, m) != 1`. If `a` is a multiple of the prime `m`, `0` has no inverse either.
13. **Reducing the exponent modulo `m`.** Exponents reduce modulo `phi(m)` (or `p - 1`), never modulo `m`.
14. **Factorials beyond the modulus.** `fact[i]` for `i >= p` is `0 mod p`; the inverse trick breaks. Keep `N < p`.
15. **Off-by-one in Pascal / nCr**: `C(n, r) = 0` for `r > n` and for `r < 0`; do not index out of range.
16. **Negative numbers and `%`/`//`.** Python's results differ from C++'s. Trust the formula `a == (a // b) * b + a % b` with `0 <= a % b < b` for positive `b`.
17. **Bit trap: operator precedence.** Put parentheses around every bitwise operation inside a comparison.
18. **Bit trap: `~n` is `-n - 1`**, not "n with 32 bits flipped". To simulate fixed width, mask with `(1 << w) - 1`.
19. **Bit trap: shift beyond the type.** There is no overflow in Python, but if the problem is defined for 32-bit integers you must mask yourself.
20. **Recomputing in a loop**: calling `pow` or `ext_gcd` inside a loop that could use one precomputed array is a common reason for time-outs. Precompute once.

## 12. Summary

- Python integers never overflow, but the modulus `10**9 + 7` (or `998244353`) is part of many problems, and reducing keeps numbers small and fast.
- `%` in Python has the **sign of the divisor**, so `x % m` is in `0 .. m-1` for positive `m`. `divmod(a, b)` gives `(a // b, a % b)`.
- Divisors come in pairs, so trial division stops at `sqrt(n)`: loop while `d * d <= n` or use `math.isqrt`. Cost O(sqrt n).
- The sieve of Eratosthenes crosses off multiples starting at `p * p`: O(n log log n). The SPF sieve factorises in O(log n) per query. The segmented sieve handles windows of huge numbers.
- Divisor count from exponents: `(e1 + 1)(e2 + 1)...`.
- `gcd(a, b) = gcd(b, a % b)`, `lcm = a // gcd * b`, both O(log n). Fold across a list.
- Extended Euclid returns `g, x, y` with `a x + b y = g`; from it come modular inverses, linear Diophantine equations, linear congruences and the CRT.
- Under a modulus: `+`, `-`, `*` can be reduced anywhere; division needs an inverse (exists iff `gcd(a, m) = 1`); exponents reduce modulo `phi(m)`.
- Fast exponentiation squares the base and reads the bits of the exponent: O(log b). In Python, `pow(a, b, m)` and `pow(a, -1, m)`.
- `nCr`: Pascal (additions only, `O(n^2)`) for small `n`; factorial + inverse factorial for large `n` with a prime modulus. Legendre: `v_p(n!) = sum n // p**k`. `phi(n) = n * prod (1 - 1/p)`.
- Bits: `n & (n - 1)` clears the lowest set bit, `n & -n` isolates it, XOR cancels pairs, bitmasks enumerate subsets. Python's negative integers behave as infinite two's complement.

## 13. How this chapter maps to the problems

Every one of the 40 problems uses one of the tools above. If a problem is stuck, go back to the section named here.

| Problems | Topic | Section |
|---|---|---|
| 1 (count divisors), 13 (why sqrt), 2 (primality), 3 (trace the divisor tests) | trial division, divisor pairs | 2, 3 |
| 4 (list primes), 5 (count primes below n), 26 (trace sieve crossing), 25 (Goldbach split) | the sieve and its boundaries | 4 |
| 14 (factorise), 15 (divisor count, many queries) | factorisation, SPF sieve, divisor formula | 3, 4 |
| 36 (segmented sieve) | segmented sieve | 4 |
| 6 (gcd), 7 (lcm), 16 (gcd of array), 17 (lcm of 1..n mod p), 22 (trace gcd/lcm table) | Euclid, LCM identity, prime powers | 5 |
| 29 (extended Euclid), 33 (trace the table), 30 (inverse for any modulus) | Bezout, extended Euclid, inverses | 6, 8 |
| 31 (explain congruence), 32 (solve congruence), 38 (CRT) | linear congruences, CRT | 6 |
| 9 (trace `%` and `//`), 8 (fast power), 21 (trace fast power), 18 (huge exponent) | modular arithmetic, exponentiation | 2, 7 |
| 27 (explain inverse conditions), 19 (factorials and inverses), 28 (fix nCr with division) | inverse, `nCr` modulo a prime | 8, 9 |
| 10 (Pascal row), 20 (explain Pascal vs factorials) | Pascal and the choice of method | 9 |
| 34 (trailing zeros of n!), 37 (phi and gcd sum) | Legendre, Euler totient | 9 |
| 11 (popcount), 12 (trace bit ops), 23 (subset sums), 24 (single number), 35 (trace shifts and `~`), 39 (two single numbers) | bit manipulation | 10 |
| 40 (build the toolkit) | everything | 3 to 10 |

Habits that win points in this module: write every formula as a short function first and test it against a brute-force version on small input (as you
saw throughout this chapter); precompute once and answer many queries; and read the constraints (`n <= 10^6`? `10^9`? `10^18`?) to choose between trial
division, a sieve, and a formula.

## 14. Learning outcomes checklist

By the end of this module you should be able to:

- [ ] Explain why trial division needs only `d * d <= n`, and write it without floats.
- [ ] Write a sieve with correct boundaries, and an SPF sieve for fast factorisation.
- [ ] Compute gcd and lcm with Euclid and explain why Euclid is correct and fast.
- [ ] Use extended Euclid to get an inverse, solve `a x + b y = c`, solve `a x == b (mod m)`, and combine two congruences.
- [ ] Reduce sums, differences and products modulo `m` at any point, and say why division and exponents are different.
- [ ] Write fast exponentiation by hand and trace it.
- [ ] Choose between Fermat and extended Euclid for an inverse, and say when no inverse exists.
- [ ] Compute `nCr` by Pascal and by factorials with inverse factorials, and say when each is right.
- [ ] Use Legendre's formula and the totient formula.
- [ ] Use `&`, `|`, `^`, shifts and masks; `n & (n - 1)`, `n & -n`; enumerate subsets by mask; use XOR to cancel pairs.
- [ ] Predict Python's behaviour for negative numbers with `%`, `//`, `~` and `>>`.

## 15. Further reading

- Python docs: the `math` module (`isqrt`, `gcd`, `lcm`, `comb`), and the built-in `pow` with three arguments.
- cp-algorithms.com: "Sieve of Eratosthenes", "Euclidean algorithm", "Extended Euclidean algorithm", "Binary exponentiation", "Modular inverse", "Chinese remainder theorem", "Euler's totient function", "Binomial coefficients".
- CSES Problem Set, "Introductory Problems" and "Mathematics" sections; practise the problems listed in `external.toml`.
