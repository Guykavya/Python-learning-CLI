import ast
from collections import Counter


def count_nodes(source):
    """Counter of AST node type names in source."""
    tree = ast.parse(source)
    # TODO: walk the tree and count type(node).__name__
    return Counter()


def uses_name(source, name):
    """True if name is used as a plain variable (an ast.Name node) in source."""
    # TODO
    return False
