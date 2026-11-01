import sys


def call_chain(stop=None, qualified=False):
    """Names of the calling functions, innermost first, up to <module> or stop."""
    frame = sys._getframe(1)
    names = []
    while frame is not None:
        code = frame.f_code
        if code.co_name == "<module>" or code.co_name == stop:
            break
        names.append(code.co_qualname if qualified else code.co_name)
        frame = frame.f_back
    del frame
    return names
