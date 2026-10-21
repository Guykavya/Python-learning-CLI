"""Starter files for `learn new`. Kept in code so they never go missing."""

from __future__ import annotations


def problem_files(pid: str, title: str, tier: str, kind: str) -> dict[str, str]:
    files = {
        "problem.toml": (
            f'id = "{pid}"\n'
            f'title = "{title}"\n'
            f'tier = "{tier}"            # drill | applied | deep | challenge\n'
            f'kind = "{kind}"            # code | trace | explain\n'
            'topics = ["TODO"]\n'
            "# difficulty = 800         # optional, defaults by tier\n"
            "# minutes = 10             # optional, defaults by tier\n"
            '# assessment = "build"     # optional: explain | trace | fix | build\n'
        ),
        "problem.md": f"# {title}\n\nTODO: describe the task, inputs, outputs and one example.\n",
        "hints.md": (
            "## Hint 1\n\nA question that points at the right idea.\n\n"
            "## Hint 2\n\nA nudge toward the approach or data structure.\n\n"
            "## Hint 3\n\nPseudocode for the hardest part only.\n"
        ),
        "solution.md": (
            "## Approach\n\nWhy this works.\n\n## Code\n\n```python\n```\n\n"
            "## Complexity\n\nTime and space.\n\n## Another way\n\nAn alternative and its trade-off.\n"
        ),
        "mistakes.md": "- A common mistake and why it is wrong.\n",
    }
    if kind == "code":
        files["starter.py"] = 'def solve():\n    """TODO"""\n    raise NotImplementedError\n'
        files["reference.py"] = "def solve():\n    return None\n"
        files["test_solution.py"] = (
            "from solution import solve\n\n\n"
            "def test_example():\n"
            '    assert solve() is None, "Explain in plain words what went wrong when this fails"\n'
        )
    elif kind == "trace":
        files["problem.md"] = (
            f"# {title}\n\nPredict exactly what this program prints. Do not run it.\n\n"
            "```python\nprint('TODO')\n```\n"
        )
        files["expected.txt"] = "TODO\n"
    else:
        files["answer.md"] = "TODO: the model answer the learner compares against.\n"
    return files
