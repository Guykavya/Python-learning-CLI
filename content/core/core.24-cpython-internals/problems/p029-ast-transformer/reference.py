"""A constant folder: an ast.NodeTransformer that computes + - * on number literals."""

import ast

OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
}


def number_value(node):
    """The value of a number literal (int or float, not bool), also written as -literal; else None."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub)
            and isinstance(node.operand, ast.Constant) and type(node.operand.value) in (int, float)):
        return -node.operand.value
    return None


def make_number(value):
    """A node for value. Negative numbers become -(positive literal), exactly as the parser makes them."""
    if value < 0:
        return ast.UnaryOp(op=ast.USub(), operand=ast.Constant(-value))
    return ast.Constant(value)


class ConstantFolder(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.folds = 0

    def visit_BinOp(self, node):
        self.generic_visit(node)  # fold the children first (bottom-up)
        operator = OPERATORS.get(type(node.op))
        left, right = number_value(node.left), number_value(node.right)
        if operator is None or left is None or right is None:
            return node
        self.folds += 1
        return ast.copy_location(make_number(operator(left, right)), node)


def fold(source):
    """Return (new_source, number_of_folds)."""
    tree = ast.parse(source)
    folder = ConstantFolder()
    tree = folder.visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree), folder.folds
