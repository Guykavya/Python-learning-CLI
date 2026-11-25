import numpy as np
import pandas as pd
import pytest

import base64
import re

from solution import Finding, render_html

PNG1 = b"\x89PNG\r\n\x1a\n" + bytes(range(40))
PNG2 = b"\x89PNG\r\n\x1a\n" + bytes(range(100, 160))


def finding(figures=("a.png", "b.png")):
    return Finding(headline="Churn <5% & rising", recommendations=[{"action": "Fix <courier> contract", "owner": "Ops & Co", "by": "31 January 2025"}],
                   impact="About 60 to 70 customers a month", evidence=["Ratio 2.9 (95% CI 2.7 to 3.1)", "1.4 points"],
                   confidence="High", limitations=["Observational", "Short window"], next_steps=["Success measure: churn < 4.5%"],
                   figures=list(figures))


@pytest.fixture
def figdir(tmp_path):
    (tmp_path / "a.png").write_bytes(PNG1)
    (tmp_path / "b.png").write_bytes(PNG2)
    return tmp_path


def test_starts_as_html_with_escaped_headline(figdir):
    page = render_html(finding(), "Data: test", figdir)
    assert page.lstrip().lower().startswith("<!doctype html>"), "the page must start with <!doctype html>."
    assert "<h1>Churn &lt;5% &amp; rising</h1>" in page, "escape the headline: '<' becomes &lt; and '&' becomes &amp;."
    assert "<5% &" not in page and "<courier>" not in page, "never put unescaped text into the page."


def test_six_sections_in_order(figdir):
    page = render_html(finding(), "Data: test", figdir)
    heads = re.findall(r"<h3>(.*?)</h3>", page)
    assert heads == ["Recommendation", "Impact", "Evidence", "Confidence", "Limitations", "Next steps"], f"six <h3> sections in order, got {heads}"


def test_lists_and_recommendation_text(figdir):
    page = render_html(finding(), "Data: test", figdir)
    assert "<li>Fix &lt;courier&gt; contract (owner: Ops &amp; Co; by 31 January 2025)</li>" in page, "recommendation item: 'action (owner: X; by Y)', escaped."
    assert page.count("<li>") == 1 + 2 + 2 + 1, "one <li> per recommendation, evidence item, limitation and next step."


def test_figures_embedded(figdir):
    page = render_html(finding(), "Data: test", figdir)
    imgs = re.findall(r"<img src='data:image/png;base64,([A-Za-z0-9+/=]+)' alt='([^']*)'>", page)
    assert [alt for _, alt in imgs] == ["a.png", "b.png"], f"one embedded <img> per figure, in order, got {[alt for _, alt in imgs]}"
    assert base64.b64decode(imgs[0][0]) == PNG1 and base64.b64decode(imgs[1][0]) == PNG2, "the base64 data must be the file's bytes."
    assert page.index("<h3>Impact</h3>") < page.index("<img") < page.index("<h3>Evidence</h3>"), "figures go after the Impact section."


def test_source_note_and_missing_figure(figdir):
    page = render_html(finding(figures=()), "Data <2024> & code", figdir)
    assert "<p><small>Data &lt;2024&gt; &amp; code</small></p>" in page, "the escaped source note goes at the end."
    assert "<img" not in page, "no figures listed: no <img>."
    with pytest.raises(FileNotFoundError):
        render_html(finding(figures=("missing.png",)), "note", figdir)
