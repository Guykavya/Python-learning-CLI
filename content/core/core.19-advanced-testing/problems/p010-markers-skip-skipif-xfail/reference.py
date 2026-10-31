import sys

import pytest


def slugify(text):
    return text.strip().lower().replace(" ", "-")


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


@pytest.mark.xfail(reason="accents are not removed yet", strict=True)
def test_slugify_accents():
    # a known bug: accents are not removed yet
    assert slugify("Cr\u00e8me Br\u00fbl\u00e9e") == "creme-brulee"


@pytest.mark.skipif(sys.version_info < (4, 0), reason="needs Python 4")
def test_needs_python_4():
    assert sys.version_info >= (4, 0)


@pytest.mark.skip(reason="not written yet")
def test_not_written_yet():
    raise NotImplementedError


@pytest.mark.slow
def test_sum_of_a_million():
    assert sum(range(1_000_000)) == 499999500000
