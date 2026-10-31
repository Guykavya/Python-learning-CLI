class HistoryMixin:
    max_history = None

    def _log(self, action, *args):
        # TODO: build the text and add it to self._history (create the list the first time)
        pass

    def history(self):
        return []

    def clear_history(self):
        pass


class Counter(HistoryMixin):
    def __init__(self, start=0):
        self.value = start

    def increment(self, by=1):
        self.value += by

    def reset(self):
        self.value = 0


class TextBox(HistoryMixin):
    def __init__(self):
        self.text = ""

    def type(self, s):
        self.text += s

    def backspace(self, n=1):
        pass

    def clear(self):
        self.text = ""
