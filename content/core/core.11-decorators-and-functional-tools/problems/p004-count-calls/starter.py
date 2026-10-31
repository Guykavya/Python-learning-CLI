def count_calls(func):
    # TODO: build a wrapper that counts its calls in wrapper.calls
    return func


@count_calls
def square(n):
    return n * n
