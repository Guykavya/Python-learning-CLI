import ast
from collections import Counter


def count_nodes(source):
    """Counter of AST node type names in source."""
    tree = ast.parse(source)
    return Counter(type(node).__name__ for node in ast.walk(tree))


def uses_name(source, name):
    """True if name is used as a plain variable (an ast.Name node) in source."""
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and node.id == name:
            return True
    return False
