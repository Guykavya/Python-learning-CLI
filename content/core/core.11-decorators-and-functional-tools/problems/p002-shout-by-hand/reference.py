def shout(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper


def greet(name):
    return "hello, " + name


loud_greet = shout(greet)
