def register(registry, name):
    def decorate(func):
        return func
    return decorate


def run_command(registry, line):
    return None


COMMANDS = {}
