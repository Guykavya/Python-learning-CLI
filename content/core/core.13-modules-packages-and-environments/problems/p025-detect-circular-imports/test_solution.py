import pytest

from solution import find_cycle, import_order

BASE = {
    "app": ["models", "views"],
    "views": ["models", "utils"],
    "models": ["db"],
    "db": ["config"],
    "config": [],
    "utils": [],
}


def check_cycle(graph, cycle):
    assert isinstance(cycle, list) and len(cycle) >= 2, "A cycle is a list like ['a', 'b', 'a']."
    assert cycle[0] == cycle[-1], "The cycle starts and ends with the same module."
    assert len(set(cycle[:-1])) == len(cycle) - 1, "Inside the cycle no module repeats (except first = last). Cut the path at the module you found again."
    for a, b in zip(cycle, cycle[1:]):
        assert b in graph.get(a, []), f"{a} does not import {b}. Every step of the cycle must follow an import arrow."


def check_order(graph, order):
    modules = set(graph) | {m for deps in graph.values() for m in deps}
    assert sorted(order) == sorted(modules), "import_order lists every module once, also modules that only appear in an import list."
    where = {m: i for i, m in enumerate(order)}
    for m, deps in graph.items():
        for d in deps:
            assert where[d] < where[m], f"{m} imports {d}, so {d} must come before {m}. Append a module only after all its imports are done."


def test_no_cycle():
    assert find_cycle(BASE) is None, "This graph has no cycle. Return None."


def test_order_example():
    order = import_order(BASE)
    check_order(BASE, order)
    assert order == ["config", "db", "models", "utils", "views", "app"], "With sorted start modules and sorted imports, the DFS finish order is config, db, models, utils, views, app."


def test_simple_cycle():
    g = dict(BASE, config=["models"])
    cycle = find_cycle(g)
    check_cycle(g, cycle)
    assert set(cycle) == {"models", "db", "config"}, "The only loop is models -> db -> config -> models."


def test_two_module_cycle():
    g = {"a": ["b"], "b": ["a"]}
    cycle = find_cycle(g)
    check_cycle(g, cycle)
    assert len(cycle) == 3, "a -> b -> a has three entries."


def test_self_import():
    g = {"a": ["a"], "b": []}
    assert find_cycle(g) == ["a", "a"], "A module that imports itself is the cycle ['a', 'a']."


def test_cycle_only_below_the_start():
    g = {"main": ["x"], "x": ["y"], "y": ["z"], "z": ["y"]}
    cycle = find_cycle(g)
    check_cycle(g, cycle)
    assert set(cycle) == {"y", "z"}, "main and x lead to the loop but are not part of it. Cut the path at the module that is in progress."


def test_diamond_is_not_a_cycle():
    g = {"top": ["left", "right"], "left": ["base"], "right": ["base"], "base": []}
    assert find_cycle(g) is None, "Reaching 'base' twice by two roads is not a cycle. Only a module still IN PROGRESS means a cycle; a DONE one is fine."
    check_order(g, import_order(g))


def test_disconnected_parts():
    g = {"a": ["b"], "b": [], "c": ["d"], "d": ["e"], "e": ["c"]}
    cycle = find_cycle(g)
    check_cycle(g, cycle)
    assert set(cycle) == {"c", "d", "e"}, "Start a search from every module that is still new, not only from the first one."


def test_targets_without_keys():
    g = {"app": ["json", "os", "helpers"], "helpers": ["os"]}
    order = import_order(g)
    check_order(g, order)
    assert find_cycle(g) is None, "Modules missing from the keys import nothing. Use graph.get(m, [])."


def test_order_raises_with_cycle():
    g = dict(BASE, config=["models"])
    with pytest.raises(ValueError) as info:
        import_order(g)
    msg = str(info.value)
    assert " -> " in msg and "models" in msg and "config" in msg and "db" in msg, "The message shows the cycle joined with ' -> ', like 'cycle: models -> db -> config -> models'."


def test_does_not_change_graph():
    g = {"b": ["a"], "a": []}
    copy = {k: list(v) for k, v in g.items()}
    import_order(g)
    find_cycle(g)
    assert g == copy, "Do not change the graph you were given (no sorting in place, no new keys)."


def test_empty_graph():
    assert find_cycle({}) is None and import_order({}) == [], "An empty graph has no cycle and an empty order."


def test_long_chain():
    g = {f"m{i:03}": [f"m{i + 1:03}"] for i in range(300)}
    order = import_order(g)
    check_order(g, order)
    g["m300"] = ["m000"]
    cycle = find_cycle(g)
    check_cycle(g, cycle)
    assert len(cycle) == 302, "The loop goes through all 301 modules and back to the start."
