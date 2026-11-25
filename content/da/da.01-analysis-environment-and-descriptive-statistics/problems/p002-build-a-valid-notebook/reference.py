def make_notebook(cells):
    out = []
    for index, (kind, text) in enumerate(cells):
        if kind not in ("markdown", "code"):
            raise ValueError(f"unknown cell kind: {kind!r}")
        cell = {"cell_type": kind, "id": f"cell-{index}", "metadata": {}, "source": text}
        if kind == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        out.append(cell)
    return {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": out}
