import inspect
import random

import pytest

import solution
from solution import Leaderboard


def board():
    lb = Leaderboard()
    lb.add("cy", 40)
    lb.add("ana", 50)
    lb.add("bo", 40)
    lb.add("dee", 30)
    return lb


def test_top():
    lb = board()
    assert lb.top(3) == [("ana", 50), ("bo", 40), ("cy", 40)], (
        "Highest score first; equal scores by name A-Z. Store (-score, name) so ascending tuples give that order."
    )
    assert lb.top(10) == [("ana", 50), ("bo", 40), ("cy", 40), ("dee", 30)], "n bigger than the board: everyone."
    assert lb.top(0) == [], "top(0) is empty."
    assert len(lb) == 4, "Four players."


def test_scores_are_positive_in_output():
    lb = board()
    assert all(score > 0 for _, score in lb.top(4)), "top() must return the real score, not the stored -score."


def test_rank_competition():
    lb = board()
    assert lb.rank("ana") == 1, "The best player has rank 1."
    assert lb.rank("bo") == 2 and lb.rank("cy") == 2, "Equal scores share a rank: both 40s are rank 2."
    assert lb.rank("dee") == 4, "Competition ranking: after two players at rank 2 comes rank 4 (1 + three strictly higher)."
    with pytest.raises(KeyError):
        lb.rank("nobody")


def test_count_at_least():
    lb = board()
    assert lb.count_at_least(40) == 3, "50, 40, 40 are >= 40: the boundary is included (bisect_right on -score)."
    assert lb.count_at_least(41) == 1, "Only 50 is >= 41."
    assert lb.count_at_least(0) == 4, "Everyone has at least 0."
    assert lb.count_at_least(51) == 0, "Nobody has 51."


def test_add_replaces():
    lb = board()
    lb.add("dee", 60)
    assert lb.top(1) == [("dee", 60)], "A new score for an existing player replaces the old one."
    assert len(lb) == 4, "Replacing must not add a second entry for 'dee'. Remove the old (-score, name) tuple first."
    lb.add("ana", 10)
    assert lb.top(5) == [("dee", 60), ("bo", 40), ("cy", 40), ("ana", 10)], "A LOWER new score also replaces the old one."
    assert lb.rank("ana") == 4, "ana is now last."


def test_remove():
    lb = board()
    lb.remove("bo")
    assert lb.top(5) == [("ana", 50), ("cy", 40), ("dee", 30)], "remove takes the player off the board."
    assert lb.rank("dee") == 3, "Ranks move up after a removal."
    with pytest.raises(KeyError):
        lb.remove("bo")


def test_remove_right_entry_with_ties():
    lb = Leaderboard()
    for name in ["e", "a", "d", "b", "c"]:
        lb.add(name, 7)
    lb.remove("c")
    assert [n for n, _ in lb.top(10)] == ["a", "b", "d", "e"], "With many equal scores, remove exactly (-score, name), not just any entry with that score."


def test_random_against_sorted():
    rng = random.Random(16)
    lb = Leaderboard()
    scores = {}
    for _ in range(400):
        name = f"p{rng.randint(0, 60)}"
        if rng.random() < 0.15 and name in scores:
            lb.remove(name)
            del scores[name]
        else:
            s = rng.randint(0, 25)
            lb.add(name, s)
            scores[name] = s
    expected = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    assert lb.top(1000) == expected, "After many adds, replaces and removes the board must equal a full sort."
    for name, s in scores.items():
        assert lb.rank(name) == 1 + sum(1 for v in scores.values() if v > s), f"rank({name!r}) is 1 + players strictly higher."
    assert len(lb) == len(scores), "One entry per player."


def test_uses_insort_not_sort():
    src = inspect.getsource(solution.Leaderboard)
    assert "insort" in src, "Insert with bisect.insort so the list stays sorted."
    assert ".sort(" not in src and "sorted(" not in src, "Do not re-sort the list; insort keeps it sorted already."
