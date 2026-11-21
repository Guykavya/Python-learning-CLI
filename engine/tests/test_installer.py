"""The installer adds the [tui] extra only when config.toml asks for full-screen mode."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("install_with_progress", ROOT / "scripts" / "install_with_progress.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


@pytest.mark.parametrize(
    "config_text, expected_suffix",
    [
        ('[ui]\nmode = "tui"\n', "[tui]"),
        ('[ui]\nmode = "plain"\n', ""),
        ('[plan]\ndaily_minutes = 60\n', ""),       # no ui section: plain
        ("this is not toml [[[", ""),                 # broken file: plain, never a crash
    ],
)
def test_tui_extra_follows_config(tmp_path, config_text, expected_suffix):
    (tmp_path / "config.toml").write_text(config_text, encoding="utf-8")
    project = str(tmp_path)
    assert installer.install_target(project) == project + expected_suffix, (
        "the installer must add [tui] only when [ui] mode is \"tui\" in config.toml"
    )


def test_no_config_file_means_plain(tmp_path):
    assert installer.install_target(str(tmp_path)) == str(tmp_path), (
        "a fresh clone has no config.toml yet; the installer must not add the extra"
    )
