import os
import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines.

    Spaces at the end of each line are ignored, and so are blank lines at the very end.
    """
    r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin, capture_output=True,
                       text=True, encoding="utf-8", timeout=10,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    lines = [line.rstrip() for line in r.stdout.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def test_example():
    assert run("HTTPS://Example.COM:8080/docs/page.html?lang=en&q=str#top\n") == [
        "Scheme: https", "Host: example.com", "Port: 8080", "Path: /docs/page.html",
        "Query: lang=en&q=str", "Fragment: top"]


def test_minimal():
    assert run("http://example.org\n") == [
        "Scheme: http", "Host: example.org", "Port: (default)", "Path: /", "Query: (none)", "Fragment: (none)"], (
        "Missing parts come out of partition as ''. Use `or` for the defaults, and the path is just '/'.")


def test_query_with_slash_and_colon():
    out = run("https://a.in/search?next=/home&t=10:30\n")
    assert out[2] == "Port: (default)", "The ':' in the query is not a port. Remove the query before looking for ':'."
    assert out[3] == "Path: /search", "The '/' in the query is not part of the path. Remove the query first."
    assert out[4] == "Query: next=/home&t=10:30"


def test_fragment_without_path():
    assert run("https://site.com#about\n") == [
        "Scheme: https", "Host: site.com", "Port: (default)", "Path: /", "Query: (none)", "Fragment: about"]


def test_port_without_path():
    assert run("ftp://Files.Example.net:21\n")[1:4] == ["Host: files.example.net", "Port: 21", "Path: /"]


def test_unicode_path_kept():
    assert run("https://wiki.org/wiki/Café?x=1\n")[3] == "Path: /wiki/Café", "Only the scheme and host are lowercased."
