from target import load_config


def clean(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_MODE", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)


def test_defaults(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    assert load_config() == {"mode": "dev", "port": 8000, "name": "app"}, "No file, no variables: defaults."


def test_environment_overrides_defaults(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    monkeypatch.setenv("APP_MODE", "prod")
    monkeypatch.setenv("APP_PORT", "9000")
    cfg = load_config()
    assert cfg["mode"] == "prod", "APP_MODE must override the default mode."
    assert cfg["port"] == 9000, "APP_PORT must override the default port and be an int, not '9000'."


def test_file_overrides_defaults_and_port_is_int(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    (tmp_path / "config.txt").write_text("name=shop\nport=7000\n", encoding="utf-8")
    cfg = load_config()
    assert cfg["name"] == "shop", "config.txt must be read from the current folder."
    assert cfg["port"] == 7000, "A port from the file must be converted to int too."


def test_environment_beats_file(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    (tmp_path / "config.txt").write_text("mode=test\nport=7000\n", encoding="utf-8")
    monkeypatch.setenv("APP_MODE", "prod")
    monkeypatch.setenv("APP_PORT", "9001")
    cfg = load_config()
    assert cfg["mode"] == "prod" and cfg["port"] == 9001, "Environment variables win over config.txt."


def test_comments_and_blank_lines_are_ignored(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    (tmp_path / "config.txt").write_text("# a comment\n\nname=x\n", encoding="utf-8")
    assert load_config() == {"mode": "dev", "port": 8000, "name": "x"}, "Comments and blank lines are not settings."


def test_spaces_around_keys_and_values_are_removed(tmp_path, monkeypatch):
    clean(monkeypatch, tmp_path)
    (tmp_path / "config.txt").write_text("  mode  =  test  \n", encoding="utf-8")
    assert load_config()["mode"] == "test", "Strip the spaces around the key and the value."
