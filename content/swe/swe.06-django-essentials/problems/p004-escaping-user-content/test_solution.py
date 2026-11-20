import pytest
from django.utils.html import escape

from solution import render_comment


def wrap(inner):
    return f'<p class="comment">{inner}</p>'


def test_plain_text_is_wrapped():
    assert render_comment("Hello world") == wrap("Hello world"), (
        "A plain comment must come back as <p class=\"comment\">Hello world</p>. "
        f"Got {render_comment('Hello world')!r}.")


def test_script_tag_is_escaped():
    out = render_comment("<script>alert(1)</script>")
    assert "<script" not in out, (
        f"A <script> tag got through unescaped: {out!r}. Render the text with {{{{ text }}}} (auto-escaping on), "
        "never paste it into the HTML yourself and never use |safe.")
    assert "&lt;script&gt;" in out, f"Expected the escaped form &lt;script&gt; in the output, got {out!r}."


@pytest.mark.parametrize("attack", [
    "<img src=x onerror=alert(1)>",
    '"><svg onload=alert(1)>',
    "<a href=\"javascript:alert(1)\">click</a>",
    "' onmouseover='alert(1)",
])
def test_attack_strings_never_become_tags(attack):
    out = render_comment(attack)
    inner = out[len('<p class="comment">'):-len("</p>")]
    assert "<" not in inner and ">" not in inner, (
        f"The text {attack!r} produced a raw < or > inside the comment: {inner!r}. All of them must be escaped.")
    assert inner == escape(attack), (
        f"Expected exactly the escaped text {escape(attack)!r}, got {inner!r}.")


def test_ampersand_is_escaped_once():
    out = render_comment("Tom & Jerry &lt;3")
    assert out == wrap("Tom &amp; Jerry &amp;lt;3"), (
        f"'&' must become '&amp;' exactly once (also in text that already looks escaped), got {out!r}.")


def test_newline_becomes_br():
    assert render_comment("one\ntwo") == wrap("one<br>two"), (
        f"A newline must become <br>, got {render_comment('one' + chr(10) + 'two')!r}. Use the linebreaksbr filter.")


def test_windows_newlines_too():
    assert render_comment("one\r\ntwo") == wrap("one<br>two"), (
        "A Windows line break (\\r\\n) must also give a single <br>. linebreaksbr handles this for you; "
        "do not replace '\\n' by hand.")


def test_html_and_newlines_together():
    out = render_comment("<b>bold</b>\nsecond")
    assert out == wrap("&lt;b&gt;bold&lt;/b&gt;<br>second"), (
        f"Escape first, then add <br>: the <br> you add is yours and must stay a real tag, got {out!r}.")


def test_url_stays_text():
    out = render_comment("see http://example.com/?a=1&b=2")
    assert "<a " not in out, f"A URL must stay plain text, not become a link (no urlize), got {out!r}."
    assert out == wrap("see http://example.com/?a=1&amp;b=2"), f"The '&' inside the URL must be escaped, got {out!r}."


def test_empty_comment():
    assert render_comment("") == wrap(""), f"An empty comment gives an empty paragraph, got {render_comment('')!r}."


def test_uses_a_template_not_the_input_as_template():
    out = render_comment("{{ 7 * 7 }} {% now 'Y' %}")
    assert "{{ 7 * 7 }}" in out, (
        f"The comment must be treated as data. Never build a Template from the visitor's text; got {out!r}.")
