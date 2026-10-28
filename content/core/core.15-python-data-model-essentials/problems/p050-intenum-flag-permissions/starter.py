from enum import Flag, IntEnum, auto


class Permission(Flag):
    pass


class Priority(IntEnum):
    pass


def describe(perm):
    return ""


def parse(text):
    return None


def allows(granted, needed):
    return False


def highest(priorities):
    return None
