"""A small copy of the chapter's make_study idea (section 10.1) for the tests: here every confounder is measured."""
import numpy as np
import pandas as pd
import pytest


def make_study(seed=70, n=5000, tau=120):
    rng = np.random.default_rng(seed)
    city = rng.choice(["Metro", "Large", "Small"], n, p=[.35, .40, .25])
    age = np.clip(rng.normal(35, 10, n), 18, 70).round()
    eng = rng.normal(0, 1, n)
    base = pd.Series(city).map({"Metro": 2700, "Large": 2200, "Small": 1700}).to_numpy()
    p_app = 1 / (1 + np.exp(-(-0.6 + 1.2 * eng - 0.02 * (age - 35) + 0.3 * (city == "Metro"))))
    app = rng.random(n) < p_app
    spend = base + 350 * eng + tau * app + rng.normal(0, 450, n)
    return pd.DataFrame({"city": city, "age": age, "engagement": eng.round(2), "app": app, "spend": spend.round(0)})


@pytest.fixture
def study_factory():
    return make_study
