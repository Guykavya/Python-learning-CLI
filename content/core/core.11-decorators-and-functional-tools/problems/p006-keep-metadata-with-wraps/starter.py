def strip_result(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).strip()
    return wrapper
