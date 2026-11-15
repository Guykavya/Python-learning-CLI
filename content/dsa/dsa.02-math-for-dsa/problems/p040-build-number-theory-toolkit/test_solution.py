import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import math
import random

P = 10 ** 9 + 7


def ask(cmds, timeout=10):
    return run(f"{len(cmds)}\n" + "\n".join(cmds) + "\n", timeout=timeout)


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def factor_str(n):
    out, p = [], 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e:
            out.append(f"{p}^{e}")
        p += 1
    if n > 1:
        out.append(f"{n}^1")
    return " ".join(out) or "1"


def phi(n):
    r, p = n, 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            r -= r // p
        p += 1
    if n > 1:
        r -= r // n
    return r


def check(cmds, want, why):
    got = ask(cmds)
    assert len(got) == len(want), (
        f"Commands {cmds}: expected {len(want)} output lines, got {len(got)}: {got}. "
        "Print exactly one line per command (also for `error` and `none`).")
    for c, g, w in zip(cmds, got, want):
        assert g == w, f"Command `{c}`: expected `{w}`, got `{g}`. {why}"


# ----- gcd and lcm
def test_gcd_basic():
    check(["gcd 12 18", "gcd 7 13", "gcd 100 75", "gcd 9 9"], ["6", "1", "25", "9"], "gcd: Euclid's loop (a, b) -> (b, a % b).")


def test_gcd_zero():
    check(["gcd 0 5", "gcd 5 0", "gcd 0 0"], ["5", "5", "0"], "gcd(0, x) = x and gcd(0, 0) = 0.")


def test_gcd_big():
    a, b = 2 ** 60 * 3, 2 ** 59 * 9
    check([f"gcd {a} {b}", "gcd 1000000000000000000 999999999999999999"], [str(math.gcd(a, b)), "1"], "gcd of numbers near 10^18: use integers only.")


def test_lcm_basic():
    check(["lcm 4 6", "lcm 7 13", "lcm 12 12", "lcm 1 9"], ["12", "91", "12", "9"], "lcm = a // gcd * b.")


def test_lcm_zero():
    check(["lcm 0 5", "lcm 5 0", "lcm 0 0"], ["0", "0", "0"], "lcm with 0 is 0, and lcm 0 0 must not divide by zero.")


def test_lcm_big():
    check(["lcm 1000000000000000000 999999999999999999"], ["999999999999999999000000000000000000"], "lcm of coprime big numbers is their product, exact: no floats.")


# ----- inv
def test_inv_exists():
    check(["inv 3 11", "inv 3 10", "inv 10 17", "inv 1 2"], ["4", "7", "12", "1"], "inv a m: x with a*x % m == 1, smallest non-negative.")


def test_inv_none():
    check(["inv 4 10", "inv 0 7", "inv 7 7", "inv 6 9"], ["none"] * 4, "no inverse when gcd(a, m) != 1: print `none`.")


def test_inv_composite_not_fermat():
    check(["inv 2 9", "inv 5 12", "inv 7 15"], ["5", "5", "13"], "The modulus may be composite: Fermat's pow(a, m - 2, m) is wrong here. Use extended Euclid.")


def test_inv_modulus_one():
    check(["inv 5 1", "inv 0 1"], ["0", "0"], "Modulo 1 the inverse is 0 (everything is 0).")


def test_inv_a_bigger_than_m():
    check(["inv 12 5", "inv 100 7"], ["3", "4"], "Reduce `a % m` first: 12 = 2 (mod 5), inverse 3; 100 = 2 (mod 7), inverse 4.")


def test_inv_huge():
    m = 10 ** 18 + 9
    a = 123456789123456789
    want = str(pow(a, -1, m)) if math.gcd(a, m) == 1 else "none"
    check([f"inv {a} {m}", "inv 3 1000000000000000000"], [want, str(pow(3, -1, 10 ** 18))], "Modulus near 10^18: loops over x are far too slow.")


def test_inv_result_in_range():
    got = ask(["inv 10 17", "inv 6 35", "inv 99 100"])
    assert got == ["12", "6", "99"], f"Got {got}. The result must be between 0 and m - 1 (take x % m after extended Euclid)."


# ----- ncr
def test_ncr_basic():
    check(["ncr 10 3 1000000007", "ncr 5 2 1000000007", "ncr 6 6 1000000007", "ncr 10 0 1000000007"], ["120", "10", "1", "1"], "ncr n r m: C(n, r) % m.")


def test_ncr_modulus_applied():
    check(["ncr 10 3 7", "ncr 10 3 100", "ncr 20 10 1000000007"], ["1", "20", str(math.comb(20, 10) % P)], "Take the remainder at the end, modulo the given m.")


def test_ncr_r_bigger_than_n():
    check(["ncr 5 7 100", "ncr 0 1 5", "ncr 3 4 1000000007"], ["0", "0", "0"], "C(n, r) = 0 when r > n.")


def test_ncr_edges():
    check(["ncr 0 0 5", "ncr 10 3 1", "ncr 1 1 2"], ["1", "0", "1"], "C(0, 0) = 1, and anything modulo 1 is 0.")


def test_ncr_big_composite_modulus():
    check(["ncr 60 30 1000", "ncr 1000 500 999999937"], [str(math.comb(60, 30) % 1000), str(math.comb(1000, 500) % 999999937)],
          "The modulus is not always prime: do not divide by multiplying with a Fermat inverse. Use Pascal's rule or exact division of the products.")


# ----- factor
def test_factor_basic():
    check(["factor 360", "factor 97", "factor 1024", "factor 12"], ["2^3 3^2 5^1", "97^1", "2^10", "2^2 3^1"], "factor n: `p^e` pairs, increasing p, space-separated, exponent always shown (also 1).")


def test_factor_one():
    check(["factor 1"], ["1"], "factor 1 prints `1`.")


def test_factor_leftover_prime():
    check(["factor 14", "factor 2002", "factor 999999999989"], ["2^1 7^1", "2^1 7^1 11^1 13^1", "999999999989^1"],
          "After the loop to sqrt(n), a leftover value > 1 is a prime factor: print it too.")


def test_factor_prime_power():
    check(["factor 999966000289", "factor 2147483648"], [factor_str(999966000289), "2^31"], "A prime squared (999983^2) needs the loop to include p * p <= n with `<=`.")


# ----- isprime
def test_isprime_small():
    check([f"isprime {n}" for n in (0, 1, 2, 3, 4, 5, 9, 25, 49, 97)], ["no", "no", "yes", "yes", "no", "yes", "no", "no", "no", "yes"],
          "0 and 1 are not prime; 4, 9, 25, 49 are squares of primes, so the loop needs `i * i <= n` (with `=`).")


def test_isprime_big():
    check(["isprime 1000000007", "isprime 999999999989", "isprime 1000000000000", "isprime 999966000289"], ["yes", "yes", "no", "no"],
          "Large inputs: trial division only up to sqrt(n). 999966000289 = 999983^2.")


# ----- phi
def test_phi():
    check(["phi 1", "phi 36", "phi 97", "phi 100", "phi 2"], ["1", "12", "96", "40", "1"], "phi(n) = n * prod (1 - 1/p), in integers: result = result // p * (p - 1).")


def test_phi_big():
    check(["phi 1000000000000", "phi 999999999989", "phi 720720"], [str(phi(10 ** 12)), "999999999988", str(phi(720720))], "No floats: n * (1 - 1/p) in floating point gives wrong answers for big n.")


# ----- pow
def test_pow_basic():
    check(["pow 2 10 1000", "pow 2 100 13", "pow 3 13 1000", "pow 5 3 7"], ["24", str(pow(2, 100, 13)), "323", "6"], "pow a b m: a^b % m.")


def test_pow_zero_cases():
    check(["pow 0 0 7", "pow 5 0 1", "pow 7 5 1", "pow 0 5 7", "pow 5 0 7"], ["1", "0", "0", "0", "1"], "x^0 = 1 (also 0^0 here), except modulo 1 where everything is 0.")


def test_pow_huge_exponent():
    check(["pow 2 1000000000000000000 1000000007", "pow 3 999999999999999999 998244353"],
          [str(pow(2, 10 ** 18, P)), str(pow(3, 10 ** 18 - 1, 998244353))], "Exponent up to 10^18: halve the exponent (binary exponentiation), do not loop b times.")


def test_pow_big_modulus():
    m = 10 ** 18 + 9
    check([f"pow 123456789123 987654321987 {m}"], [str(pow(123456789123, 987654321987, m))], "Big modulus: the product of two residues is up to 10^36, fine for Python ints.")


# ----- popcount
def test_popcount():
    check(["popcount 255", "popcount 0", "popcount 1", "popcount 1024", "popcount 1023"], ["8", "0", "1", "1", "10"], "popcount n: number of 1 bits.")


def test_popcount_wide():
    check([f"popcount {2 ** 40 - 1}", f"popcount {2 ** 62 + 1}", f"popcount {2 ** 64 - 1}"], ["40", "2", "64"], "n can have more than 32 bits: do not stop after 31 or 32 shifts.")


# ----- sieve
def test_sieve():
    check(["sieve 30", "sieve 2", "sieve 10"], ["2 3 5 7 11 13 17 19 23 29", "2", "2 3 5 7"], "sieve n: all primes up to AND INCLUDING n, space-separated.")


def test_sieve_none():
    check(["sieve 1", "sieve 0"], ["none", "none"], "No primes: print `none`.")


def test_sieve_inclusive_square():
    check(["sieve 49", "sieve 29", "sieve 3"], [" ".join(str(p) for p in range(2, 50) if is_prime(p)), " ".join(str(p) for p in range(2, 30) if is_prime(p)), "2 3"],
          "n itself counts (29 is prime), and so does a prime square limit (49 needs crossing off with 7).")


def test_sieve_big():
    got = ask(["sieve 1000000"], timeout=10)
    assert len(got) == 1 and len(got[0].split()) == 78498 and got[0].split()[-1] == "999983", (
        "sieve 1000000 must list all 78498 primes, the last is 999983. If it timed out, use a sieve, not trial division.")


# ----- errors and format
def test_unknown_command():
    check(["hello 1 2", "GCD 4 6", "gcdd 4 6"], ["error"] * 3, "An unknown command name prints `error` (case matters). Never crash.")


def test_wrong_argument_count():
    check(["gcd 4", "gcd 4 6 8", "factor", "ncr 5 2", "isprime 3 4", "popcount"], ["error"] * 6, "Wrong number of arguments: `error`.")


def test_not_a_number():
    check(["gcd a b", "gcd 4 x", "factor 3.5", "isprime -7", "gcd -4 6"], ["error"] * 5, "Arguments must be non-negative integers: letters, decimals and negatives give `error`.")


def test_domain_errors():
    check(["inv 3 0", "pow 2 3 0", "ncr 5 2 0", "factor 0", "phi 0"], ["error"] * 5, "Modulus 0 and n = 0 for factor/phi are errors, not crashes (no ZeroDivisionError).")


def test_blank_line_is_error():
    got = ask(["gcd 4 6", "", "gcd 6 9"])
    assert got == ["2", "error", "3"], f"Got {got}. A blank command line counts as one command and prints `error`."


def test_extra_spaces():
    got = ask(["  gcd   12    18 ", "isprime    97"])
    assert got == ["6", "yes"], f"Got {got}. Split on any amount of whitespace: `line.split()` with no argument."


def test_state_does_not_leak():
    got = ask(["factor 12", "factor 7", "sieve 10", "sieve 5", "gcd 4 6", "gcd 9 6"])
    assert got == ["2^2 3^1", "7^1", "2 3 5 7", "2 3 5", "2", "3"], f"Got {got}. Each command must start fresh: no variable carried from the previous command."


def test_mixed_session():
    cmds = ["gcd 12 18", "inv 3 11", "ncr 10 3 1000000007", "factor 360", "isprime 97", "phi 36", "pow 2 100 13", "popcount 255", "sieve 30", "lcm 4 6"]
    want = ["6", "4", "120", "2^3 3^2 5^1", "yes", "12", str(pow(2, 100, 13)), "8", "2 3 5 7 11 13 17 19 23 29", "12"]
    check(cmds, want, "The sample session from the statement.")


# ----- differential and speed
def oracle(c):
    w = c.split()
    n = w[0]
    v = list(map(int, w[1:]))
    if n == "gcd":
        return str(math.gcd(*v))
    if n == "lcm":
        return str(math.lcm(*v))
    if n == "inv":
        return "none" if math.gcd(v[0] % v[1], v[1]) != 1 else str(pow(v[0], -1, v[1]) if v[1] > 1 else 0)
    if n == "ncr":
        return str(math.comb(v[0], v[1]) % v[2])
    if n == "factor":
        return factor_str(v[0])
    if n == "isprime":
        return "yes" if is_prime(v[0]) else "no"
    if n == "phi":
        return str(phi(v[0]))
    if n == "pow":
        return str(pow(v[0], v[1], v[2]))
    return str(bin(v[0]).count("1"))


def test_random_session():
    rng = random.Random(40)
    cmds = []
    for _ in range(300):
        n = rng.choice(["gcd", "lcm", "inv", "ncr", "factor", "isprime", "phi", "pow", "popcount"])
        if n in ("gcd", "lcm"):
            cmds.append(f"{n} {rng.randint(0, 10 ** 12)} {rng.randint(0, 10 ** 12)}")
        elif n == "inv":
            cmds.append(f"inv {rng.randint(0, 10 ** 9)} {rng.randint(1, 10 ** 9)}")
        elif n == "ncr":
            nn = rng.randint(0, 300)
            cmds.append(f"ncr {nn} {rng.randint(0, nn + 3)} {rng.randint(1, 10 ** 9)}")
        elif n in ("factor", "phi"):
            cmds.append(f"{n} {rng.randint(1, 10 ** 8)}")
        elif n == "isprime":
            cmds.append(f"isprime {rng.randint(0, 10 ** 8)}")
        elif n == "pow":
            cmds.append(f"pow {rng.randint(0, 10 ** 9)} {rng.randint(0, 10 ** 18)} {rng.randint(1, 10 ** 9)}")
        else:
            cmds.append(f"popcount {rng.randint(0, 2 ** 64)}")
    got = ask(cmds, timeout=20)
    assert len(got) == len(cmds), "One output line per command."
    for c, g in zip(cmds, got):
        assert g == oracle(c), f"Command `{c}`: expected `{oracle(c)}`, got `{g}`."


def test_speed_many_big_primes():
    cmds = ["isprime 999999999989", "isprime 1000000007", "factor 999999999989", "phi 999999999989"] * 5 + ["sieve 1000000"]
    got = ask(cmds, timeout=15)
    assert len(got) == len(cmds), (
        "Too slow or missing output. Trial division must stop at sqrt(n) (about 10^6 steps for n = 10^12, not 10^12) and "
        "the sieve must be a sieve.")
