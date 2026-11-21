import pytest

from solution import explain_exit


@pytest.mark.parametrize("code, expected", [
    (0, "0: success"),
    (1, "1: the application reported a general error"),
    (2, "2: usage error (bad arguments)"),
    (126, "126: the command was found but could not be executed (permissions)"),
    (127, "127: command not found"),
])
def test_fixed_codes(code, expected):
    assert explain_exit(code) == expected, f"Exit code {code} has a fixed text; expected {expected!r}."


def test_sigkill_is_137():
    assert explain_exit(137) == "137: killed by signal 9 (SIGKILL); often the out-of-memory killer: check OOMKilled and the stop timeout", \
        "137 = 128 + 9 = SIGKILL, with the out-of-memory hint appended after '; '."


def test_sigterm_is_143():
    assert explain_exit(143) == "143: killed by signal 15 (SIGTERM); the process was asked to stop", "143 = 128 + 15 = SIGTERM."


@pytest.mark.parametrize("code, n, name", [(129, 1, "SIGHUP"), (130, 2, "SIGINT"), (131, 3, "SIGQUIT"), (134, 6, "SIGABRT"), (139, 11, "SIGSEGV")])
def test_other_signals(code, n, name):
    assert explain_exit(code) == f"{code}: killed by signal {n} ({name})", \
        f"{code} - 128 = {n}, which is {name}. Only 137 and 143 get an extra sentence."


def test_unknown_signal():
    assert explain_exit(150) == "150: killed by signal 22 (unknown name)", "128 + 22: signal 22 is not in SIGNALS."
    assert explain_exit(192) == "192: killed by signal 64 (unknown name)"


@pytest.mark.parametrize("code", [3, 4, 100, 125, 128, 193, 255])
def test_application_codes(code):
    assert explain_exit(code) == f"{code}: application-specific error code", \
        f"{code} is not 0, 1, 2, 126, 127 or 129-192, so it is the application's own code. Note 128 itself is not 128 + n."


@pytest.mark.parametrize("code", [-1, 256, 1000])
def test_out_of_range(code):
    with pytest.raises(ValueError):
        explain_exit(code)
