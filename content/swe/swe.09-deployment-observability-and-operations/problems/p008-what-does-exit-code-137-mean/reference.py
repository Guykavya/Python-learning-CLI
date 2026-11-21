SIGNALS = {1: "SIGHUP", 2: "SIGINT", 3: "SIGQUIT", 6: "SIGABRT", 9: "SIGKILL", 11: "SIGSEGV", 15: "SIGTERM"}

FIXED = {
    0: "0: success",
    1: "1: the application reported a general error",
    2: "2: usage error (bad arguments)",
    126: "126: the command was found but could not be executed (permissions)",
    127: "127: command not found",
}


def explain_exit(code):
    if not 0 <= code <= 255:
        raise ValueError(f"an exit code is between 0 and 255, got {code}")
    if code in FIXED:
        return FIXED[code]
    if 129 <= code <= 192:
        n = code - 128
        text = f"{code}: killed by signal {n} ({SIGNALS.get(n, 'unknown name')})"
        if code == 137:
            text += "; often the out-of-memory killer: check OOMKilled and the stop timeout"
        elif code == 143:
            text += "; the process was asked to stop"
        return text
    return f"{code}: application-specific error code"
