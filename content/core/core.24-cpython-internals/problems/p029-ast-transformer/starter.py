"""A constant folder: an ast.NodeTransformer that computes + - * on number literals."""

import ast


class ConstantFolder(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.folds = 0

    def visit_BinOp(self, node):
        # TODO: fold the children first, then this node if both sides are number literals
        return node


def fold(source):
    """Return (new_source, number_of_folds)."""
    tree = ast.parse(source)
    folder = ConstantFolder()
    tree = folder.visit(tree)
    return ast.unparse(tree), folder.folds
