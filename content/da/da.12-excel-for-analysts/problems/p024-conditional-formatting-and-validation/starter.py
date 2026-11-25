from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation


def add_checks(ws, n_rows, target, regions, input_cell="H1"):
    """Highlight margins below target in D2:D{n+1} and add a region dropdown on input_cell."""
    raise NotImplementedError
