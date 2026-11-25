import numpy as np
import pandas as pd
import pytest

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parent / "solution.py")


def run_app():
    return AppTest.from_file(APP, default_timeout=30).run()


def test_default_view():
    at = run_app()
    assert not at.exception, f"the app raised: {[e.value for e in at.exception]}"
    assert at.title[0].value == "Revenue by city", "title 'Revenue by city'."
    assert at.multiselect[0].label == "City" and at.multiselect[0].value == ["Large", "Metro", "Small"], "City multiselect with all sorted cities selected."
    assert [m.label for m in at.metric] == ["Revenue"], "one metric labelled Revenue."
    assert at.metric[0].value == "3,350", f"total revenue of all cities is 3,350, got {at.metric[0].value!r}"


def test_selecting_one_city():
    at = run_app()
    at.multiselect[0].set_value(["Metro"]).run()
    assert at.metric[0].value == "2,000", f"Metro alone: 1,200 + 800 = 2,000, got {at.metric[0].value!r}"


def test_empty_selection_shows_a_message():
    at = run_app()
    at.multiselect[0].set_value([]).run()
    assert not at.exception, "an empty selection must not crash the app."
    assert [i.value for i in at.info] == ["Select at least one city."], "show the info message."
    assert len(at.metric) == 0, "no metric when nothing is selected (a 0 would be misleading)."


def test_uses_the_data_it_is_given():
    def app():
        import pandas as pd
        from solution import main
        main(pd.DataFrame({"city": ["X", "Y", "Y"], "revenue": [1000.0, 2500.0, 500.0]}))

    at = AppTest.from_function(app, default_timeout=30).run()
    assert at.multiselect[0].options == ["X", "Y"], "the options come from the data passed to main."
    assert at.metric[0].value == "4,000", f"total of the given table is 4,000, got {at.metric[0].value!r}"
