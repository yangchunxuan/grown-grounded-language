"""Self-contained smoke tests for the minimal RTC companion repo.

(1) every RTC module imports cleanly from a fresh checkout, and
(2) the no-oracle redline holds: the g1f harness's static scan finds no
    forbidden ground-truth access in the decision path.
Run:  python -m pytest tests/ -q   (from the repo root)
"""
import importlib

import pytest

RTC_MODULES = [
    "config.prereg_rtc",
    "rtc_world", "rtc_language", "rtc_metabolism", "rtc_fusion", "rtc_perception",
    "offscreen.rtc_g1_run",
    "offscreen.rtc_g0_run",
    "offscreen.rtc_g1b_scripted_run",
    "offscreen.rtc_g1c_spatial",
    "offscreen.rtc_g1d_lethal",
    "offscreen.rtc_g1e_emerge",
    "offscreen.rtc_g1f_coevolve",
    "offscreen.rtc_g1f_commblind_control",
]


@pytest.mark.parametrize("module", RTC_MODULES)
def test_imports_clean(module):
    importlib.import_module(module)


def test_no_oracle_redline_clean():
    """The g1f harness ships a static redline scan; it must find zero hits."""
    from offscreen import rtc_g1f_coevolve as g
    hits = g._redline_scan()
    assert not hits, f"no-oracle redline violated: {hits}"
