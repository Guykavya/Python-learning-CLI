from solution import sku_codes


def test_basic():
    assert list(sku_codes("tee", ["S", "M"], ["red", "blue"])) == [
        "TEE-S-RED", "TEE-S-BLUE", "TEE-M-RED", "TEE-M-BLUE"
    ], "Sizes on the outside, colours on the inside, all upper case: product(sizes, colours)."


def test_unavailable():
    assert list(sku_codes("tee", ["S", "M"], ["red", "blue"], unavailable=[("M", "red")])) == [
        "TEE-S-RED", "TEE-S-BLUE", "TEE-M-BLUE"
    ], "Skip pairs listed in unavailable. Compare before you upper-case."


def test_unavailable_as_set():
    codes = list(sku_codes("cap", ["L"], ["black", "white"], unavailable={("L", "white")}))
    assert codes == ["CAP-L-BLACK"], "unavailable may be any collection, also a set."


def test_count():
    codes = list(sku_codes("hoodie", ["S", "M", "L", "XL"], ["red", "blue", "grey", "black", "green"]))
    assert len(codes) == 20, "4 sizes x 5 colours = 20 codes."
    assert len(set(codes)) == 20, "Every code must be different."


def test_empty_sizes():
    assert list(sku_codes("tee", [], ["red"])) == [], "No sizes, no codes."


def test_is_lazy():
    result = sku_codes("tee", ["S"], ["red"])
    assert iter(result) is result, "sku_codes must give a generator (use yield, or return a generator expression), not a list."
