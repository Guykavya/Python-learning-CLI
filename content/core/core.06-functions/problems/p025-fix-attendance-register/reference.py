def mark_present(name, register=None):
    """Add name to register (a new one if none is given) unless present. Return the register."""
    if register is None:
        register = []
    if name not in register:
        register.append(name)
    return register


def absent_students(all_students, register):
    """Return a NEW list of students not in register, in all_students order. Change nothing."""
    return [name for name in all_students if name not in register]


def sorted_register(register):
    """Return a NEW list of the names sorted ignoring case. The register keeps its order."""
    return sorted(register, key=str.lower)
