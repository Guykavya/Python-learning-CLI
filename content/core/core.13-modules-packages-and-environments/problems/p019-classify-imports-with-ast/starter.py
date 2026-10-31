import ast
import sys


def find_imports(source):
    # TODO: parse with ast, walk every node, collect top-level names of absolute imports
    return []


def classify_imports(source, local=()):
    # TODO: sort each import into stdlib / third_party / local
    return {"stdlib": [], "third_party": [], "local": []}
