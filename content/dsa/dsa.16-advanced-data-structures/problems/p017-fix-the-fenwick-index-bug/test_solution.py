import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent

# Every check runs in a separate process with a time limit: the broken add(0, ...) loops forever.


def run(code, limit=10):
    try:
        r = subprocess.run([sys.executable, "-c", "from solution import Fenwick\n" + code], cwd=HERE,
                           capture_output=True, text=True, timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None
    return r


def test_index_zero_does_not_hang():
    r = run("fw = Fenwick(5)\nfw.add(0, 7)\nprint(fw.range_sum(0, 1), fw.range_sum(0, 5))\n")
    assert r is not None, (
        "add(0, ...) never finished: with i = 0, i & -i (and i & i) is 0, so i never changes. The user's index is "
        "0-based but the cells are 1-based: start the loop at i + 1.")
    assert r.returncode == 0, r.stderr[-600:]
    assert r.stdout.split() == ["7", "7"], f"a[0] = 7: expected 7 7, got {r.stdout.split()}."


def test_example():
    r = run("fw = Fenwick(5)\nfw.add(0, 7)\nfw.add(2, 5)\n"
            "print(fw.range_sum(0, 5), fw.range_sum(1, 3), fw.range_sum(0, 1))\n")
    assert r is not None, "The program hangs (see the index-0 test)."
    assert r.stdout.split() == ["12", "5", "7"], f"Expected 12 5 7, got {r.stdout.split()} {r.stderr[-300:]}"


def test_the_step_is_the_lowest_bit():
    r = run("fw = Fenwick(16)\nfw.add(2, 1)\nprint(fw.t)\n")
    assert r is not None, "The program hangs."
    t = eval(r.stdout.strip())
    touched = [k for k in range(1, 17) if t[k]]
    assert touched == [3, 4, 8, 16], (
        f"add(2, 1) on n = 16 must touch the cells 3, 4, 8, 16 (1-indexed 3 plus the lowest bit each time), "
        f"got {touched}. i & i is i: use i & -i.")


def test_random_against_list():
    code = (
        "import random\n"
        "rng = random.Random(1617)\n"
        "bad = 0\n"
        "for _ in range(100):\n"
        "    n = rng.randint(1, 40)\n"
        "    a = [0] * n\n"
        "    fw = Fenwick(n)\n"
        "    for _ in range(40):\n"
        "        i, v = rng.randrange(n), rng.randint(-9, 9)\n"
        "        a[i] += v\n"
        "        fw.add(i, v)\n"
        "        l = rng.randint(0, n)\n"
        "        r = rng.randint(l, n)\n"
        "        bad += fw.range_sum(l, r) != sum(a[l:r])\n"
        "print(bad)\n"
    )
    r = run(code, 30)
    assert r is not None, "The program hangs on random operations (index 0 or the step)."
    assert r.stdout.split() == ["0"], f"{r.stdout.strip()} wrong range sums out of 4000. {r.stderr[-300:]}"
