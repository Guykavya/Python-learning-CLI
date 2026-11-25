"""A small copy of the chapter's make_app_world (section 8.3) for the tests."""
import numpy as np
import pandas as pd
import pytest


def make_app_world(n=4000, tau=150, seed=60):
    rng = np.random.default_rng(seed)
    engagement = rng.normal(0, 1, n)
    income = rng.normal(0, 1, n)
    p_app = 1 / (1 + np.exp(-(-0.3 + 1.2 * engagement + 0.6 * income)))      # keen, well-off customers install the app
    app = rng.random(n) < p_app
    spend = 2500 + 400 * engagement + 300 * income + tau * app + rng.normal(0, 500, n)
    return pd.DataFrame({"engagement": engagement, "income": income, "app": app, "spend": spend})


@pytest.fixture
def world_factory():
    return make_app_world
