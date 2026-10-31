# Add the right markers so the checker's run gives exactly the outcomes in problem.md.
# Do NOT change what the test functions do.
import sys

import pytest


def slugify(text):
    return text.strip().lower().replace(" ", "-")


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_accents():
    # a known bug: accents are not removed yet
    assert slugify("Cr\u00e8me Br\u00fbl\u00e9e") == "creme-brulee"


def test_needs_python_4():
    assert sys.version_info >= (4, 0)


def test_not_written_yet():
    raise NotImplementedError


def test_sum_of_a_million():
    assert sum(range(1_000_000)) == 499999500000
