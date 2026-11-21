from pathlib import Path

import pytest

from solution import load, to_bool


@pytest.fixture
def toml(tmp_path):
    def write(text):
        p = tmp_path / "tidy.toml"
        p.write_text(text, encoding="utf-8")
        return p
    return write


def test_defaults_only(tmp_path):
    s, unknown = load(tmp_path / "missing.toml", env={})
    assert (s.keep_days, s.dry_run, s.log_level) == (30, True, "WARNING"), "A missing file is fine: use the defaults."
    assert s.folder == Path("~/Downloads").expanduser(), "Expand '~' in the folder."
    assert unknown == [] and set(s.sources.values()) == {"default"}


def test_file_overrides_defaults(toml):
    s, _ = load(toml('folder = "/data/inbox"\nkeep_days = 14\ndry_run = false\nlog_level = "info"\n'), env={})
    assert (s.folder, s.keep_days, s.dry_run, s.log_level) == (Path("/data/inbox"), 14, False, "INFO"), \
        "Values from the TOML file beat the defaults; log_level is upper-cased."
    assert s.sources == {"folder": "file", "keep_days": "file", "dry_run": "file", "log_level": "file"}


def test_env_overrides_file_and_is_converted(toml):
    s, _ = load(toml("keep_days = 14\ndry_run = true\n"), env={"TIDY_KEEP_DAYS": "7", "TIDY_DRY_RUN": "No"})
    assert s.keep_days == 7 and isinstance(s.keep_days, int), "The environment beats the file, and '7' becomes the int 7."
    assert s.dry_run is False, "'No' is False: bool('No') would be True, so use to_bool."
    assert s.sources["keep_days"] == "env" and s.sources["dry_run"] == "env"


def test_empty_env_counts_as_not_set(toml):
    s, _ = load(toml('folder = "/data/inbox"\n'), env={"TIDY_FOLDER": ""})
    assert s.folder == Path("/data/inbox") and s.sources["folder"] == "file", \
        "TIDY_FOLDER='' must not override: an empty path would mean 'the current folder'."


def test_flags_beat_everything_but_none_means_not_given(toml):
    s, _ = load(toml("keep_days = 14\n"), env={"TIDY_KEEP_DAYS": "7", "TIDY_DRY_RUN": "yes"},
                flags={"keep_days": None, "dry_run": False, "log_level": "debug"})
    assert s.keep_days == 7, "keep_days=None in flags means 'not typed': the environment value stays."
    assert s.dry_run is False and s.sources["dry_run"] == "flag", "dry_run=False is a real choice: it beats the env 'yes'."
    assert s.log_level == "DEBUG" and s.sources["log_level"] == "flag"


def test_zero_from_a_flag_is_kept(toml):
    s, _ = load(toml("keep_days = 14\n"), env={}, flags={"keep_days": 0})
    assert s.keep_days == 0, "0 is a value, not 'missing': test 'is not None', not truthiness."


def test_unknown_keys_are_reported(toml):
    s, unknown = load(toml('kep_days = 7\nfolder = "/x"\napi_token = "abc"\nzzz = 1\n'), env={})
    assert unknown == ["api_token", "kep_days", "zzz"], f"Report unknown keys (sorted), including api_token; got {unknown}"
    assert s.keep_days == 30 and s.api_token is None, "Unknown keys are not used, and the token never comes from the file."


def test_token_only_from_env_and_hidden(tmp_path):
    s, _ = load(None, env={"TIDY_API_TOKEN": "s3cret"})
    assert s.api_token == "s3cret"
    assert "s3cret" not in repr(s), "The token must not appear in repr (field(repr=False))."
    assert load(None, env={"TIDY_API_TOKEN": ""})[0].api_token is None, "An empty token is no token."


def test_bad_values_name_the_setting_and_source(toml):
    with pytest.raises(ValueError, match="keep_days from env"):
        load(None, env={"TIDY_KEEP_DAYS": "ten"})
    with pytest.raises(ValueError, match="dry_run from file"):
        load(toml('dry_run = "maybe"\n'), env={})
    with pytest.raises(ValueError, match="log_level from flag"):
        load(None, env={}, flags={"log_level": "loud"})


@pytest.mark.parametrize("value, expected", [(True, True), (False, False), ("1", True), ("YES", True), ("on", True),
                                             ("0", False), ("False", False), ("off", False)])
def test_to_bool(value, expected):
    assert to_bool(value) is expected


def test_to_bool_refuses_other_words():
    with pytest.raises(ValueError):
        to_bool("maybe")


def test_os_environ_is_the_default(monkeypatch):
    monkeypatch.setenv("TIDY_KEEP_DAYS", "3")
    s, _ = load(None)
    assert s.keep_days == 3, "env=None means: read os.environ."
