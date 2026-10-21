import pytest
from solution import island_sizes, count_islands
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


GRID = ["##..#",
        "#...#",
        "..#..",
        "....#"]


def test_example():
    assert island_sizes(GRID) == [3, 2, 1, 1], "Sizes of the islands, largest first."
    assert count_islands(GRID) == 4


def test_empty_and_water():
    assert count_islands([]) == 0 and island_sizes([]) == []
    assert count_islands(["...", "..."]) == 0


def test_diagonal_not_connected():
    assert island_sizes(["#.", ".#"]) == [1, 1], "Diagonal cells are NOT connected."


def test_edges_do_not_wrap():
    assert count_islands(["#..#"]) == 2, (
        "Check bounds BEFORE indexing: grid[r][-1] wraps around to the other edge in Python.")
    assert count_islands(["#", ".", "#"]) == 2


def test_snake():
    snake = ["#####",
             "....#",
             "#####",
             "#....",
             "#####"]
    assert island_sizes(snake) == [17]


def test_big_island():
    big = ["#" * 20 for _ in range(20)]
    assert island_sizes(big) == [400]


def test_two_grids_in_a_row():
    assert count_islands(["#"]) == 1
    assert count_islands(["#"]) == 1, "The second call found nothing: is the visited set shared between calls?"


def test_grid_unchanged():
    g = list(GRID)
    island_sizes(g)
    assert g == GRID


def test_recursive():
    recursive = [n.name for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef)
                 and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == n.name
                         for c in ast.walk(n))]
    assert recursive, "Use a recursive flood-fill function."
