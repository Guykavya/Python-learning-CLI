import pytest

from solution import hanoi


def replay(n, moves, source="A", target="C", spare="B"):
    """Play the moves on real pegs and fail with a clear message on the first illegal one."""
    pegs = {source: list(range(n, 0, -1)), target: [], spare: []}
    for step, move in enumerate(moves, 1):
        assert isinstance(move, tuple) and len(move) == 2, f"Move {step} is {move!r}: every move must be a tuple (from_peg, to_peg)."
        a, b = move
        assert a in pegs and b in pegs, f"Move {step} {move} uses a peg that does not exist (pegs are {sorted(pegs)})."
        assert pegs[a], f"Move {step} {move} takes a disc from the empty peg {a}."
        disc = pegs[a][-1]
        assert not pegs[b] or pegs[b][-1] > disc, (
            f"Move {step} {move} puts disc {disc} on the smaller disc {pegs[b][-1]}. "
            "Check the order of the peg arguments in your two recursive calls.")
        pegs[b].append(pegs[a].pop())
    assert pegs[target] == list(range(n, 0, -1)), f"After all moves the tower is not complete on peg {target}: {pegs}."


def test_zero():
    assert hanoi(0) == [], "hanoi(0) needs no moves: return []. This is the natural base case."


def test_one():
    assert hanoi(1) == [("A", "C")], "One disc moves straight from source to target."


def test_two_exact():
    assert hanoi(2) == [("A", "B"), ("A", "C"), ("B", "C")], \
        "For two discs: small to the spare, big to the target, small on top of it."


def test_three_exact():
    want = [("A", "C"), ("A", "B"), ("C", "B"), ("A", "C"), ("B", "A"), ("B", "C"), ("A", "C")]
    assert hanoi(3) == want, "The shortest solution for 3 discs is unique; yours differs. Replay it on paper."


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8, 10])
def test_legal_and_shortest(n):
    moves = hanoi(n)
    assert len(moves) == 2 ** n - 1, f"hanoi({n}) must use exactly 2^{n} - 1 = {2 ** n - 1} moves, got {len(moves)}."
    replay(n, moves)


def test_custom_peg_names():
    moves = hanoi(3, "X", "Y", "Z")
    assert len(moves) == 7, "3 discs need 7 moves."
    replay(3, moves, source="X", target="Y", spare="Z")


def test_fifteen():
    moves = hanoi(15)
    assert len(moves) == 2 ** 15 - 1, "15 discs need 32767 moves."
    replay(15, moves)
