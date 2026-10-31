import importlib.util
from pathlib import Path


def load_plugins(folder):
    # TODO: for each public .py file (sorted), load it fresh with importlib.util,
    # collect callable `register` functions, and list the files that failed to load
    return {}, []


def run_plugins(folder, app):
    # TODO: call every register(app) in sorted order, return the stems
    return []
