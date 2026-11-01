import sys


def call_chain(stop=None, qualified=False):
    """Names of the calling functions, innermost first, up to <module> or stop."""
    frame = sys._getframe(1)  # the caller's frame
    names = []
    # TODO: follow frame.f_back until <module>, stop, or None
    return names
