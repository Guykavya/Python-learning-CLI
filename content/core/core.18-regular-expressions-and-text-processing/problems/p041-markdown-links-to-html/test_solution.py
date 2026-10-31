from solution import md_links


def test_single_link():
    assert md_links("[home](/)") == '<a href="/">home</a>', "Capture the text and the url, then build <a href=\"url\">text</a> with \\2 and \\1 in the replacement."


def test_example_two_links():
    got = md_links("See [the docs](https://docs.python.org) and [PEP 8](pep8.html).")
    want = 'See <a href="https://docs.python.org">the docs</a> and <a href="pep8.html">PEP 8</a>.'
    assert got == want, "Two links on one line must stay two links. A greedy .* inside [ ] or ( ) runs on to the LAST ] or ); use [^\\]]+ and [^)\\s]+ instead."


def test_text_with_spaces_kept():
    assert md_links("[a b c](x)") == '<a href="x">a b c</a>', "Link text may contain spaces."


def test_image_left_alone():
    assert md_links("![logo](logo.png)") == "![logo](logo.png)", "An image starts with '!' and must not change. A negative lookbehind (?<!!) before \\[ does it."


def test_image_and_link_mixed():
    assert md_links("![logo](logo.png) [home](/)") == '![logo](logo.png) <a href="/">home</a>', "Skip the image, convert the link next to it."


def test_space_between_parts_is_not_a_link():
    s = "[not a link] (because of the space)"
    assert md_links(s) == s, "The ( must come right after the ]. Do not allow \\s* between them."


def test_url_without_spaces():
    s = "[x](has space)"
    assert md_links(s) == s, "A url cannot contain whitespace, so this is not a link. Use [^)\\s]+ for the url."


def test_empty_parts_not_links():
    assert md_links("[](x)") == "[](x)", "Empty link text is not a link: use + not * for the text."
    assert md_links("[x]()") == "[x]()", "An empty url is not a link: use + not * for the url."


def test_no_links():
    s = "plain text, (brackets) and [squares] only"
    assert md_links(s) == s, "Text without links comes back unchanged."


def test_multiline():
    s = "1. [a](a.html)\n2. [b](b.html)\n"
    assert md_links(s) == '1. <a href="a.html">a</a>\n2. <a href="b.html">b</a>\n', "Convert links on every line; keep the newlines."


def test_link_after_exclamation_word():
    assert md_links("Wow! [yes](y)") == 'Wow! <a href="y">yes</a>', "Only a '!' directly before '[' makes an image. Here there is a space between them."
