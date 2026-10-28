import ast
from pathlib import Path


def stub_variables(path):
    # TODO: module-level AnnAssign nodes -> {name: ast.unparse(annotation)}
    return {}


def stub_functions(path):
    # TODO: FunctionDef / AsyncFunctionDef at module level and inside classes -> {name: [signature, ...]}
    return {}


def stub_untyped(path):
    # TODO: qualified names of functions that are not fully annotated
    return []


def stub_classes(path):
    # TODO: {class name: [base class text, ...]}
    return {}
