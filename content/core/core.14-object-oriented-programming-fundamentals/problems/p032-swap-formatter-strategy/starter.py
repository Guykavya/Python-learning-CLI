class PlainFormatter:
    def format(self, title, headers, rows):
        return ""


class MarkdownFormatter:
    def format(self, title, headers, rows):
        return ""


class CsvFormatter:
    def __init__(self, sep=","):
        self.sep = sep

    def format(self, title, headers, rows):
        return ""


class Report:
    def __init__(self, title, headers, rows, formatter=None):
        # TODO: store everything, check row lengths, default formatter
        pass

    def add_row(self, *values):
        pass

    def render(self, formatter=None):
        return ""
