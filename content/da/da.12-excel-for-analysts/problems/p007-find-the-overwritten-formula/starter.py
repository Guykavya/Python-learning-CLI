from openpyxl.formula.translate import Translator


def column_consistency(ws, col, first_row=2):
    """[(row, content)] of the cells below first_row that are not the first row's formula copied down."""
    raise NotImplementedError
