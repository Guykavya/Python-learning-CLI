def shout(func):
    def wrapper(*args, **kwargs):
        return None
    return wrapper


def greet(name):
    return ""


loud_greet = shout(greet)
