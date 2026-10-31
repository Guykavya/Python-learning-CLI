def register(registry, name):
    def decorate(func):
        if name in registry:
            raise ValueError(f"command already registered: {name}")
        registry[name] = func
        return func
    return decorate


def run_command(registry, line):
    parts = line.split()
    if not parts:
        raise ValueError("empty command")
    name = parts[0]
    if name not in registry:
        raise ValueError(f"unknown command: {name}")
    numbers = [int(word) for word in parts[1:]]
    return registry[name](*numbers)


COMMANDS = {}


@register(COMMANDS, "add")
def add(a, b):
    return a + b


@register(COMMANDS, "neg")
def neg(a):
    return -a


@register(COMMANDS, "total")
def total(*nums):
    return sum(nums)
