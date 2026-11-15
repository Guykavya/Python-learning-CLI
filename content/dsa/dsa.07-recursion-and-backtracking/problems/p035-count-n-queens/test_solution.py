import pytest

from solution import total_n_queens

KNOWN = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92, 9: 352}


@pytest.mark.parametrize("n", range(1, 10))
def test_known_counts(n):
    got = total_n_queens(n)
    want = KNOWN[n]
    hint = ""
    if got > want:
        hint = " Too many: check both diagonals (r - c and r + c) and remove from the sets after the call."
    elif got < want:
        hint = " Too few: did you forget to remove a column or diagonal from its set when backtracking?"
    assert got == want, f"total_n_queens({n}) should be {want}, got {got}.{hint}"


def test_repeatable():
    assert total_n_queens(6) == 4 and total_n_queens(6) == 4, "Calling twice must give the same answer: do not keep sets between calls."
