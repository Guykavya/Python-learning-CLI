from enum import Flag, IntEnum, auto


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


def describe(perm):
    return "".join(
        letter if flag in perm else "-"
        for letter, flag in (("r", Permission.READ), ("w", Permission.WRITE), ("x", Permission.EXECUTE))
    )


def parse(text):
    if len(text) != 3:
        raise ValueError(f"expected 3 characters like 'rw-', got {text!r}")
    result = Permission(0)
    for char, expected, flag in zip(text, "rwx", (Permission.READ, Permission.WRITE, Permission.EXECUTE)):
        if char == expected:
            result |= flag
        elif char != "-":
            raise ValueError(f"bad character {char!r} in {text!r}")
    return result


def allows(granted, needed):
    return needed in granted


def highest(priorities):
    return max(priorities, default=None)
