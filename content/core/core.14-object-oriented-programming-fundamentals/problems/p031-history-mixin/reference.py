class HistoryMixin:
    """Adds an action log to any class. Defines no __init__ on purpose."""

    max_history = None

    def _log(self, action, *args):
        if "_history" not in vars(self):
            self._history = []
        text = ", ".join(repr(arg) for arg in args)
        self._history.append(f"{action}({text})")
        if self.max_history is not None and len(self._history) > self.max_history:
            del self._history[: len(self._history) - self.max_history]

    def history(self):
        return list(vars(self).get("_history", []))

    def clear_history(self):
        self._history = []


class Counter(HistoryMixin):
    def __init__(self, start=0):
        self.value = start

    def increment(self, by=1):
        self.value += by
        self._log("increment", by)

    def reset(self):
        self.value = 0
        self._log("reset")


class TextBox(HistoryMixin):
    max_history = 5

    def __init__(self):
        self.text = ""

    def type(self, s):
        self.text += s
        self._log("type", s)

    def backspace(self, n=1):
        self.text = self.text[: max(len(self.text) - n, 0)]
        self._log("backspace", n)

    def clear(self):
        self.text = ""
        self._log("clear")
