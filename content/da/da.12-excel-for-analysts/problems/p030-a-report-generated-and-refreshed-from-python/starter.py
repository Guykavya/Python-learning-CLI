import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.workbook.properties import CalcProperties


def build_report(orders, products, target_margin=0.40):
    """Workbook with sheets Summary, Orders, Products, Inputs: formulas, defined names, SUMIFS grid, conditional format (see the statement)."""
    raise NotImplementedError
