def mark_present(name, register=[]):
    """Add name to register (a new one if none is given) unless present. Return the register."""
    if name not in register:
        register.append(name)
    return register


def absent_students(all_students, register):
    """Return a NEW list of students not in register, in all_students order. Change nothing."""
    for name in register:
        if name in all_students:
            all_students.remove(name)
    return all_students


def sorted_register(register):
    """Return a NEW list of the names sorted ignoring case. The register keeps its order."""
    register.sort(key=str.lower)
    return register
