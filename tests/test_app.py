"""Smoke test of the starter dashboard (app/dashboard.py): it runs, and the range warning follows the inputs."""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "app" / "dashboard.py")


def test_dashboard_runs_and_flags_follow_the_inputs():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    # default scenario 2 moves 10% of the TV budget to influencers: above any level ever held
    assert len(at.error) == 1 and "TV to influencers" in at.error[0].value and "Influencers" in at.error[0].value
    assert len(at.metric) == 2 and " to " in at.metric[0].value
    at.slider(key="s1_influencer").set_value(0).run()
    assert not at.exception and len(at.error) == 0 and len(at.success) == 1
    at.sidebar.radio[0].set_value(3).run()
    assert not at.exception and len(at.metric) == 3
