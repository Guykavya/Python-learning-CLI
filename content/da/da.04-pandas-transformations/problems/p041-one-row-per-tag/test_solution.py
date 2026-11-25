import pandas as pd

from solution import tag_counts


def products():
    return pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"],
        "category": ["home", "home", "toys", "toys", "office", "beauty", "grocery", "toys"],
        "tags": ["eco, gift", "gift", "", None, "eco,kids , gift", "kids", " eco ", "toys,"],
    })


def test_columns_and_index():
    out = tag_counts(products())
    assert list(out.columns) == ["tag", "products"], "the columns are tag and products; got %s" % list(out.columns)
    assert out.index.tolist() == list(range(len(out))), "fresh index 0, 1, ..."


def test_counts():
    got = dict(zip(tag_counts(products())["tag"], tag_counts(products())["products"]))
    assert "" not in got, "empty tags (from '' and the trailing comma in 'toys,') must be ignored"
    assert " gift" not in got and " eco " not in got, "strip the spaces around each tag"
    assert got.get("eco") == 3, "eco is on P1, P5 and P7 (' eco ' after stripping): 3; got %s" % got.get("eco")
    assert got.get("gift") == 3, "gift is on P1, P2 and P5: 3"
    assert got.get("kids") == 2, "kids is on P5 ('kids ' with a space) and P6: 2 (did you split at ', ' with the space?)"
    assert got.get("toys") == 1, "toys,: one tag 'toys' plus an empty one to ignore"
    assert len(got) == 4, "exactly four tags: eco, gift, kids, toys; got %s" % sorted(got)


def test_order():
    out = tag_counts(products())
    assert out["tag"].tolist() == ["eco", "gift", "kids", "toys"], (
        "sort by count descending, then tag alphabetically (eco before gift: both 3)")
    assert out["products"].tolist() == [3, 3, 2, 1]


def test_no_tags_at_all():
    p = pd.DataFrame({"product_id": ["P1", "P2"], "tags": ["", None]})
    out = tag_counts(p)
    assert len(out) == 0, "no product has a real tag: the result is empty"
    assert list(out.columns) == ["tag", "products"], "an empty result still has the columns tag and products"


def test_input_unchanged():
    p = products()
    before = p.copy()
    tag_counts(p)
    pd.testing.assert_frame_equal(p, before, obj="products")
