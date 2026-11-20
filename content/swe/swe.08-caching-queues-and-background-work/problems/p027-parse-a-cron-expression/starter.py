from datetime import datetime, timedelta

FIELDS = [("minute", 0, 59), ("hour", 0, 23), ("day", 1, 31), ("month", 1, 12), ("weekday", 0, 6)]


def parse_field(text, low, high, name="field"):
    # TODO: lists, *, ranges, steps; ValueError naming the field
    return set()


class Cron:
    def __init__(self, expression):
        self.expression = expression

    def next_after(self, after):
        # TODO
        return after

    def between(self, start, end):
        return iter(())
