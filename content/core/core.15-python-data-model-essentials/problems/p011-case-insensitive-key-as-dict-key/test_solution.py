from solution import HeaderName


def test_equal_ignoring_case():
    assert HeaderName("Content-Type") == HeaderName("CONTENT-TYPE"), "Header names equal ignoring case. Compare casefold()ed texts."
    assert HeaderName("a") != HeaderName("b"), "Different names are not equal."


def test_casefold_not_lower():
    assert HeaderName("STRASSE") == HeaderName("stra\u00dfe"), "Use casefold(): it maps 'ß' to 'ss'. lower() does not."


def test_original_text_kept():
    h = HeaderName("Content-Type")
    assert h.text == "Content-Type", "Keep the original text in .text; only the comparison ignores case."
    assert str(h) == "Content-Type", "str() should be the original text."


def test_repr():
    assert repr(HeaderName("Content-Type")) == "HeaderName('Content-Type')", "repr should be HeaderName('Content-Type')."


def test_equal_objects_equal_hashes():
    assert hash(HeaderName("Accept")) == hash(HeaderName("ACCEPT")), "Equal objects must have equal hashes. Hash the casefolded text."


def test_usable_as_dict_key():
    d = {HeaderName("Content-Type"): "text/html"}
    assert d[HeaderName("CONTENT-TYPE")] == "text/html", "Lookup with a different spelling must find the value (hash AND eq must agree)."
    d[HeaderName("content-type")] = "json"
    assert len(d) == 1, "Setting an equal key must replace the old entry, not add a second one."
    assert d[HeaderName("Content-Type")] == "json", "The value should have been replaced."


def test_usable_in_set():
    s = {HeaderName("A"), HeaderName("a"), HeaderName("B")}
    assert len(s) == 2, "A set must treat 'A' and 'a' as one element."


def test_not_equal_to_plain_str():
    assert not (HeaderName("a") == "a"), "Only HeaderName objects are equal to HeaderName objects: return NotImplemented for others."
    assert HeaderName("a").__eq__("a") is NotImplemented, "Return NotImplemented for non-HeaderName values."
