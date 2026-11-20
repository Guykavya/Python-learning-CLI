import random

from solution import insert_interval


def model(intervals, new):
    """Merge everything again from scratch (touching merges)."""
    out = []
    for s, e in sorted([tuple(iv) for iv in intervals] + [tuple(new)]):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def norm(result):
    return [list(iv) for iv in result]


def test_examples():
    assert norm(insert_interval([(1, 3), (6, 9)], (2, 5))) == [[1, 5], [6, 9]], (
        "(2,5) overlaps (1,3): they become [1,5]. (6,9) starts after 5 and stays.")
    assert norm(insert_interval([(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], (4, 8))) == [[1, 2], [3, 10], [12, 16]], (
        "(4,8) swallows (3,5), (6,7) and (8,10): the new block is [min start, max end] = [3,10]. Keep absorbing "
        "while a block starts at or before the new end.")


def test_positions():
    assert norm(insert_interval([(3, 5)], (0, 1))) == [[0, 1], [3, 5]], (
        "The new block goes BEFORE everything: it must be added even when no block overlaps it.")
    assert norm(insert_interval([(3, 5)], (7, 9))) == [[3, 5], [7, 9]], (
        "The new block goes AFTER everything: remember to append it when the loop ends.")
    assert norm(insert_interval([(1, 2), (8, 9)], (4, 5))) == [[1, 2], [4, 5], [8, 9]], (
        "The new block goes in a gap between two blocks, in sorted position.")
    assert norm(insert_interval([(1, 10)], (3, 4))) == [[1, 10]], (
        "The new block lies inside an existing one: nothing changes. Use min of starts and max of ends.")
    assert norm(insert_interval([(2, 3), (5, 6), (8, 9)], (0, 20))) == [[0, 20]], (
        "The new block covers every block: the answer is the new block alone.")


def test_touching_merges():
    assert norm(insert_interval([(3, 5)], (5, 6))) == [[3, 6]], (
        "(5,6) touches [3,5] at 5: touching intervals merge, as in merge intervals. A block that ENDS at the new "
        "start is not 'before' it: use end < new start for the first group.")
    assert norm(insert_interval([(3, 5)], (1, 3))) == [[1, 5]], (
        "(1,3) touches [3,5] at 3: they merge. Absorb a block when its start <= new end.")
    assert norm(insert_interval([(1, 2), (4, 5)], (2, 4))) == [[1, 5]], (
        "(2,4) touches both [1,2] and [4,5]: all three merge into [1,5].")


def test_empty_and_input_kept():
    assert norm(insert_interval([], (4, 7))) == [[4, 7]], "An empty calendar: the answer is the new block."
    data = [[1, 3], [6, 9]]
    insert_interval(data, (2, 5))
    assert data == [[1, 3], [6, 9]], "Do not change the caller's list (or its inner lists). Build a new list."


def test_random_against_merge_again():
    rng = random.Random(8)
    for _ in range(600):
        blocks = []
        x = rng.randint(-3, 3)
        for _ in range(rng.randint(0, 6)):
            s = x + rng.randint(1, 3)
            e = s + rng.randint(0, 3)
            blocks.append((s, e))
            x = e
        a = rng.randint(-4, x + 4)
        new = (a, a + rng.randint(0, 6))
        expected = model(blocks, new)
        got = norm(insert_interval(list(blocks), new))
        assert got == expected, (
            f"intervals={blocks}, new={new}: expected {expected}, got {got}. Copy blocks with end < new start, "
            "absorb blocks with start <= new end (min/max), add the new block, copy the rest.")


def test_large_input_is_fast():
    blocks = [(3 * i, 3 * i + 1) for i in range(100_000)]
    got = insert_interval(blocks, (150_001, 150_003))
    assert len(got) == 99_999 and [150_000, 150_004] in norm(got[49_990:50_010]), (
        "100,000 blocks: (150001,150003) touches [150000,150001] and [150003,150004], so 3 blocks become 1. "
        "One pass over the list is enough; do not insert into the middle of a list in a loop.")
