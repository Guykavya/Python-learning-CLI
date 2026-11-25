import numpy as np
import pandas as pd
import pytest

from pathlib import Path

import streamlit as st
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parent / "solution.py")


def fresh():
    st.cache_data.clear()                     # the cache lives in this process: start every test empty
    return AppTest.from_file(APP, default_timeout=30).run()


def test_app_shows_the_rows():
    at = fresh()
    assert not at.exception, f"the app raised: {[e.value for e in at.exception]}"
    assert at.selectbox[0].label == "Rows" and list(at.selectbox[0].options) == ["10", "100", "1000"]
    assert at.metric[0].label == "Rows loaded" and at.metric[0].value == "10", f"metric 'Rows loaded' = 10, got {at.metric[0].value!r}"


def test_reruns_do_not_reload():
    at = fresh()
    at.run()
    at.run()
    assert at.session_state["load_calls"] == 1, f"three runs with n = 10 must load once (@st.cache_data), counted {at.session_state['load_calls']} calls."


def test_one_real_call_per_distinct_argument():
    at = fresh()
    at.selectbox[0].select(100).run()
    assert at.metric[0].value == "100"
    at.selectbox[0].select(10).run()
    at.selectbox[0].select(100).run()
    assert at.session_state["load_calls"] == 2, f"n = 10 and n = 100 are two distinct arguments: 2 real loads, counted {at.session_state['load_calls']}."
    assert at.metric[0].value == "100", "the cached result is still the right data."
