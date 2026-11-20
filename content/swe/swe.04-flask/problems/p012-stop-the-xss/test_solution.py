from bs4 import BeautifulSoup
from markupsafe import Markup

from solution import create_app, format_comment


def test_returns_markup():
    assert isinstance(format_comment("hi"), Markup), "Return Markup(...), otherwise the template escapes your <strong> tags again."


def test_script_is_escaped():
    out = str(format_comment("<script>alert(1)</script>"))
    assert "<script>" not in out, f"The user's tag is still live: {out!r}. Escape the text first."
    assert out == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_bold():
    assert str(format_comment("a **b** c")) == "a <strong>b</strong> c", "**word** must become <strong>word</strong>."


def test_two_bold_parts_use_the_shortest_match():
    assert str(format_comment("**a** and **b**")) == "<strong>a</strong> and <strong>b</strong>", "Use a non-greedy pattern: \\*\\*(.+?)\\*\\*"


def test_newline_becomes_br():
    assert str(format_comment("one\ntwo")) == "one<br>two"


def test_escape_happens_before_formatting():
    out = str(format_comment("**<b>x</b>**"))
    assert out == "<strong>&lt;b&gt;x&lt;/b&gt;</strong>", f"got {out!r}: escape FIRST, then add <strong>."


def test_quotes_and_ampersands():
    out = str(format_comment('Tom & "Jerry"'))
    assert "&amp;" in out and '"' not in out, f"& and quotes must be escaped too, got {out!r}."


def test_page_is_safe():
    comments = [
        {"author": "<img src=x onerror=alert(1)>", "text": "<script>alert(1)</script> **hi**\nbye"},
        {"author": "Asha", "text": "plain"},
    ]
    app = create_app({"TESTING": True, "COMMENTS": comments})
    html = app.test_client().get("/").get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")
    assert soup.find("script") is None, "A <script> element exists on the page: XSS."
    assert soup.find("img") is None, "The author name must be escaped too (normal autoescape: no |safe)."
    first = soup.select(".comment")[0]
    assert first.select_one(".text strong").get_text() == "hi", "The bold formatting must still work on the page."
    assert first.select_one(".text br") is not None
    assert "<script>alert(1)</script>" in first.select_one(".text").get_text(), "The script text should be visible, as plain characters."
