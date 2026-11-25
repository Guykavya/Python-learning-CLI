import sys, pathlib, tempfile, re, io, datetime as dt
import numpy as np
import pandas as pd
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils.datetime import to_excel, from_excel
from openpyxl.workbook.defined_name import DefinedName


import math
from decimal import Decimal, ROUND_HALF_UP
from openpyxl.utils import column_index_from_string


class XlError(Exception):
    """An Excel error value such as #N/A or #DIV/0!. Raising it makes errors propagate through formulas, like in Excel."""
    def __init__(self, code):
        super().__init__(code)
        self.code = code

    def __repr__(self):
        return self.code

    def __eq__(self, other):
        return isinstance(other, XlError) and other.code == self.code

    def __hash__(self):
        return hash(self.code)


TOKEN = re.compile(r"""\s*(?:
  (?P<str>"(?:[^"]|"")*")|
  (?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)|
  (?P<func>[A-Za-z_][\w.]*(?=\())|
  (?P<ref>(?:(?:'[^']+'|[A-Za-z_][\w.]*)!)?\$?[A-Za-z]{1,3}\$?\d+(?::\$?[A-Za-z]{1,3}\$?\d+)?|(?:(?:'[^']+'|[A-Za-z_][\w.]*)!)?\$?[A-Za-z]{1,3}:\$?[A-Za-z]{1,3})|
  (?P<name>[A-Za-z_][\w.]*)|
  (?P<op><>|<=|>=|[-+*/^&=<>(),%])
)""", re.X)


def tokenize(s):
    pos, out = 0, []
    while pos < len(s):
        m = TOKEN.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip() == "":
                break
            raise XlError("#NAME?")
        pos = m.end()
        kind = m.lastgroup
        out.append((kind, m.group(kind)))
    return out


class Parser:
    """Excel precedence, lowest to highest: comparison, &, + -, * /, ^, unary minus, %."""
    def __init__(self, text):
        self.t = tokenize(text)
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        node = self.comparison()
        if self.i != len(self.t):
            raise XlError("#NAME?")
        return node

    def comparison(self):
        n = self.concat()
        while self.peek()[0] == "op" and self.peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
            op = self.take()[1]
            n = ("bin", op, n, self.concat())
        return n

    def concat(self):
        n = self.additive()
        while self.peek() == ("op", "&"):
            self.take()
            n = ("bin", "&", n, self.additive())
        return n

    def additive(self):
        n = self.term()
        while self.peek()[0] == "op" and self.peek()[1] in ("+", "-"):
            op = self.take()[1]
            n = ("bin", op, n, self.term())
        return n

    def term(self):
        n = self.power()
        while self.peek()[0] == "op" and self.peek()[1] in ("*", "/"):
            op = self.take()[1]
            n = ("bin", op, n, self.power())
        return n

    def power(self):
        n = self.unary()
        while self.peek() == ("op", "^"):
            self.take()
            n = ("bin", "^", n, self.unary())
        return n

    def unary(self):
        if self.peek()[0] == "op" and self.peek()[1] in ("-", "+"):
            op = self.take()[1]
            return ("un", op, self.unary())
        n = self.primary()
        while self.peek() == ("op", "%"):
            self.take()
            n = ("bin", "/", n, ("num", 100.0))
        return n

    def primary(self):
        kind, val = self.take()
        if kind == "num":
            return ("num", float(val))
        if kind == "str":
            return ("str", val[1:-1].replace('""', '"'))
        if kind == "func":
            self.take()
            args = []
            if self.peek() != ("op", ")"):
                while True:
                    args.append(self.comparison() if self.peek() not in (("op", ","), ("op", ")")) else ("blank",))
                    if self.peek() == ("op", ","):
                        self.take()
                        continue
                    break
            if self.take() != ("op", ")"):
                raise XlError("#NAME?")
            return ("call", val.upper(), args)
        if kind == "ref":
            return ("ref", val)
        if kind == "name":
            if val.upper() in ("TRUE", "FALSE"):
                return ("bool", val.upper() == "TRUE")
            return ("name", val)
        if (kind, val) == ("op", "("):
            n = self.comparison()
            if self.take() != ("op", ")"):
                raise XlError("#NAME?")
            return n
        raise XlError("#NAME?")


class Rng:
    """A rectangular block of cells on one sheet."""
    def __init__(self, book, sheet, r1, c1, r2, c2):
        self.book, self.sheet, self.r1, self.c1, self.r2, self.c2 = book, sheet, r1, c1, r2, c2

    def rows(self, raw=False):
        get = self.book.cell_raw if raw else self.book.cell                 # raw: give back error values instead of raising them
        return [[get(self.sheet, r, c) for c in range(self.c1, self.c2 + 1)] for r in range(self.r1, self.r2 + 1)]

    def flat(self, raw=False):
        return [v for row in self.rows(raw) for v in row]

    @property
    def shape(self):
        return (self.r2 - self.r1 + 1, self.c2 - self.c1 + 1)


def _num(v):
    if isinstance(v, XlError):
        raise v
    if v is None or v == "":
        return 0.0
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            raise XlError("#VALUE!")
    raise XlError("#VALUE!")


def _text(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        return str(int(v)) if v == int(v) and abs(v) < 1e15 else repr(v)
    return str(v)


def _wild(pattern):
    out, i = "", 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "~" and i + 1 < len(pattern):
            out += re.escape(pattern[i + 1])
            i += 2
            continue
        out += ".*" if ch == "*" else "." if ch == "?" else re.escape(ch)
        i += 1
    return re.compile("^" + out + "$", re.I | re.S)


def _eq_num(v, num):
    if isinstance(v, bool) or v is None:
        return False
    if isinstance(v, (int, float)):
        return float(v) == num
    if isinstance(v, str):                                   # COUNTIF treats a text "5" as the number 5
        try:
            return float(v.strip()) == num
        except ValueError:
            return False
    return False


def crit_pred(c):
    """The test that SUMIFS / COUNTIFS / AVERAGEIFS apply to each cell, built from one criterion value."""
    if isinstance(c, XlError):
        raise c
    if c is None:
        c = 0.0                                              # a criterion that refers to an empty cell means 0
    if isinstance(c, bool):
        return lambda v: v is c
    if isinstance(c, (int, float)):
        return lambda v: _eq_num(v, float(c))
    m = re.match(r"^(<=|>=|<>|<|>|=)?(.*)$", str(c), re.S)
    op, operand = m.group(1) or "=", m.group(2)
    try:
        num = float(operand)
    except ValueError:
        num = None
    if num is not None:
        if op == "=":
            return lambda v: _eq_num(v, num)
        if op == "<>":
            return lambda v: not _eq_num(v, num)
        cmp = {"<": lambda a: a < num, ">": lambda a: a > num, "<=": lambda a: a <= num, ">=": lambda a: a >= num}[op]
        return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and cmp(v)
    if operand == "" and op == "=":
        return lambda v: v is None or v == ""
    if operand == "" and op == "<>":
        return lambda v: not (v is None or v == "")
    rx = _wild(operand)
    if op == "=":
        return lambda v: isinstance(v, str) and bool(rx.match(v))
    if op == "<>":
        return lambda v: not (isinstance(v, str) and bool(rx.match(v)))
    cmp = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b}[op]
    return lambda v: isinstance(v, str) and cmp(v.lower(), operand.lower())


def xl_round(x, n=0):
    """Excel's ROUND: the value is taken at 15 significant digits, and halves go AWAY from zero."""
    d = Decimal(format(float(x), ".15g"))
    if n >= 0:
        return float(d.quantize(Decimal(1).scaleb(-int(n)), rounding=ROUND_HALF_UP))
    f = Decimal(10) ** -int(n)
    return float((d / f).quantize(Decimal(1), rounding=ROUND_HALF_UP) * f)


def _eq(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a.lower() == b.lower()
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return float(a) == float(b)
    return a == b


class Book:
    """A small formula engine for a subset of Excel. It exists so that formulas can be tested offline; Excel is the final authority."""
    def __init__(self, wb):
        self.wb = wb
        self.raw, self.memo, self.stack, self.maxrow = {}, {}, set(), {}
        for ws in wb.worksheets:
            d = {}
            for r, row in enumerate(ws.iter_rows(values_only=True), 1):
                for c, v in enumerate(row, 1):
                    if v is not None:
                        d[(r, c)] = v
            self.raw[ws.title] = d
            self.maxrow[ws.title] = ws.max_row
        self.names = {n.lower(): dn.attr_text for n, dn in wb.defined_names.items()}

    def cell(self, sheet, r, c):
        key = (sheet, r, c)
        if key in self.memo:
            v = self.memo[key]
            if isinstance(v, XlError):
                raise v
            return v
        v = self.raw[sheet].get((r, c))
        if isinstance(v, str) and v.startswith("="):
            if key in self.stack:
                raise XlError("#REF!")
            self.stack.add(key)
            try:
                try:
                    v = self.eval_node(Parser(v[1:]).parse(), sheet)
                    if isinstance(v, Rng):
                        v = v.flat()[0]
                except XlError as e:
                    self.memo[key] = e
                    raise
            finally:
                self.stack.discard(key)
        elif isinstance(v, (dt.datetime, dt.date)):
            v = float(to_excel(v))
        elif isinstance(v, int) and not isinstance(v, bool):
            v = float(v)
        self.memo[key] = v
        return v

    def cell_raw(self, sheet, r, c):
        try:
            return self.cell(sheet, r, c)
        except XlError as e:
            return e

    def value(self, sheet, coord):
        """The calculated value of a cell, or an XlError object."""
        m = re.match(r"^([A-Za-z]+)(\d+)$", coord)
        try:
            return self.cell(sheet, int(m.group(2)), column_index_from_string(m.group(1).upper()))
        except XlError as e:
            return e

    def rng(self, text, sheet):
        if "!" in text:
            sh, ref = text.rsplit("!", 1)
            sheet = sh.strip("'")
        else:
            ref = text
        parts = ref.replace("$", "").upper().split(":")

        def split(p):
            m = re.match(r"^([A-Z]+)(\d*)$", p)
            return column_index_from_string(m.group(1)), (int(m.group(2)) if m.group(2) else None)
        c1, r1 = split(parts[0])
        c2, r2 = split(parts[-1])
        if r1 is None:
            r1, r2 = 1, self.maxrow[sheet]
        return Rng(self, sheet, r1, c1, r2 if r2 else r1, c2)

    def eval_formula(self, formula, sheet):
        try:
            v = self.eval_node(Parser(formula.lstrip("=")).parse(), sheet)
            return v.flat()[0] if isinstance(v, Rng) else v
        except XlError as e:
            return e

    def scalar(self, v):
        if isinstance(v, Rng):
            if v.shape != (1, 1):
                raise XlError("#VALUE!")
            return v.flat()[0]
        return v

    def eval_node(self, n, sheet):
        k = n[0]
        if k in ("num", "str", "bool"):
            return n[1]
        if k == "blank":
            return None
        if k == "ref":
            return self.rng(n[1], sheet)
        if k == "name":
            ref = self.names.get(n[1].lower())
            if ref is None:
                raise XlError("#NAME?")
            return self.rng(ref, sheet)
        if k == "un":
            v = _num(self.scalar(self.eval_node(n[2], sheet)))
            return -v if n[1] == "-" else v
        if k == "bin":
            a, b = self.scalar(self.eval_node(n[2], sheet)), self.scalar(self.eval_node(n[3], sheet))
            op = n[1]
            if op == "&":
                return _text(a) + _text(b)
            if op in ("=", "<>", "<", ">", "<=", ">="):
                return self.compare(op, a, b)
            x, y = _num(a), _num(b)
            if op == "/":
                if y == 0:
                    raise XlError("#DIV/0!")
                return x / y
            return {"+": x + y, "-": x - y, "*": x * y}.get(op) if op != "^" else x ** y
        if k == "call":
            return self.call(n[1], n[2], sheet)
        raise XlError("#NAME?")

    def compare(self, op, a, b):
        if isinstance(a, str) and isinstance(b, str):
            a, b = a.lower(), b.lower()
        elif isinstance(a, str) != isinstance(b, str):
            if op == "=":
                return False
            if op == "<>":
                return True
            a, b = (1, 0) if isinstance(a, str) else (0, 1)
        else:
            a, b = (0 if a is None else a), (0 if b is None else b)
        return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]

    def numbers(self, args, sheet):
        out = []
        for a in args:
            v = self.eval_node(a, sheet)
            if isinstance(v, Rng):
                for x in v.flat():
                    if isinstance(x, XlError):
                        raise x
                    if isinstance(x, (int, float)) and not isinstance(x, bool):
                        out.append(float(x))
            else:
                out.append(_num(v))
        return out

    def call(self, name, args, sheet):
        ev = lambda i: self.eval_node(args[i], sheet)
        sc = lambda i: self.scalar(ev(i))
        if name == "IF":
            cond = sc(0)
            if isinstance(cond, str):
                raise XlError("#VALUE!")
            return ev(1) if (cond if isinstance(cond, bool) else bool(_num(cond))) else (ev(2) if len(args) > 2 else False)
        if name in ("IFERROR", "IFNA"):
            try:
                v = ev(0)
                return self.scalar(v) if isinstance(v, Rng) and v.shape == (1, 1) else v
            except XlError as e:
                if name == "IFNA" and e.code != "#N/A":
                    raise
                return ev(1)
        if name == "SUM":
            return sum(self.numbers(args, sheet))
        if name == "AVERAGE":
            nums = self.numbers(args, sheet)
            if not nums:
                raise XlError("#DIV/0!")
            return sum(nums) / len(nums)
        if name == "COUNT":
            return float(len(self.numbers(args, sheet)))
        if name == "COUNTA":
            return float(sum(1 for a in args for x in (lambda v: v.flat() if isinstance(v, Rng) else [v])(self.eval_node(a, sheet)) if x is not None and x != ""))
        if name == "MIN":
            nums = self.numbers(args, sheet)
            return min(nums) if nums else 0.0
        if name == "MAX":
            nums = self.numbers(args, sheet)
            return max(nums) if nums else 0.0
        if name == "ABS":
            return abs(_num(sc(0)))
        if name == "ROUND":
            return xl_round(_num(sc(0)), int(_num(sc(1))))
        if name == "ISERROR":
            try:
                sc(0)
                return False
            except XlError:
                return True
        if name == "TRIM":
            return re.sub(" +", " ", _text(sc(0))).strip(" ")
        if name == "TEXT":
            return self.text_fmt(sc(0), _text(sc(1)))
        if name == "DATE":
            return float(to_excel(dt.datetime(int(_num(sc(0))), int(_num(sc(1))), int(_num(sc(2))))))
        if name == "YEAR":
            return float(from_excel(_num(sc(0))).year)
        if name == "MONTH":
            return float(from_excel(_num(sc(0))).month)
        if name in ("SUMIFS", "COUNTIFS", "AVERAGEIFS", "SUMIF", "COUNTIF"):
            return self.ifs(name, args, sheet)
        if name == "LARGE":
            nums = sorted(self.numbers(args[:1], sheet), reverse=True)
            k = int(_num(sc(1)))
            if not 1 <= k <= len(nums):
                raise XlError("#NUM!")
            return nums[k - 1]
        if name == "MATCH":
            return self.match(args, sheet)
        if name == "INDEX":
            return self.index(args, sheet)
        if name == "XLOOKUP":
            return self.xlookup(args, sheet)
        if name == "VLOOKUP":
            return self.vlookup(args, sheet)
        raise XlError("#NAME?")

    def text_fmt(self, v, fmt):
        x = _num(v)
        simple = {"0": lambda: str(int(xl_round(x))), "0.0": lambda: f"{xl_round(x, 1):.1f}", "0.00": lambda: f"{xl_round(x, 2):.2f}",
                  "#,##0": lambda: f"{xl_round(x):,.0f}", "0%": lambda: f"{xl_round(x * 100):.0f}%", "0.0%": lambda: f"{xl_round(x * 100, 1):.1f}%"}
        if fmt in simple:
            return simple[fmt]()
        dates = {"yyyy-mm": "%Y-%m", "yyyy-mm-dd": "%Y-%m-%d", "mmm yyyy": "%b %Y"}
        if fmt in dates:
            return from_excel(x).strftime(dates[fmt])
        raise XlError("#VALUE!")

    def ifs(self, name, args, sheet):
        ev = lambda i: self.eval_node(args[i], sheet)
        if name in ("SUMIF", "COUNTIF"):
            crit_ranges, crits = [ev(0)], [self.scalar(ev(1))]
            sum_range = ev(2) if (name == "SUMIF" and len(args) > 2) else (ev(0) if name == "SUMIF" else None)
        elif name == "COUNTIFS":
            crit_ranges, crits = [ev(i) for i in range(0, len(args), 2)], [self.scalar(ev(i)) for i in range(1, len(args), 2)]
            sum_range = None
        else:
            sum_range = ev(0)
            crit_ranges, crits = [ev(i) for i in range(1, len(args), 2)], [self.scalar(ev(i)) for i in range(2, len(args), 2)]
        for r in crit_ranges + ([sum_range] if sum_range is not None else []):
            if not isinstance(r, Rng):
                raise XlError("#VALUE!")
        shape = crit_ranges[0].shape
        if any(r.shape != shape for r in crit_ranges) or (sum_range is not None and sum_range.shape != shape):
            raise XlError("#VALUE!")
        preds = [crit_pred(c) for c in crits]
        cols = [r.flat(raw=True) for r in crit_ranges]                                  # an error cell in a criteria range simply does not match
        sums = sum_range.flat(raw=True) if sum_range is not None else None             # an error in a MATCHING row of the sum range is an error
        total, count = 0.0, 0
        for i in range(len(cols[0])):
            if all(p(c[i]) for p, c in zip(preds, cols)):
                if sums is None:
                    count += 1
                    continue
                v = sums[i]
                if isinstance(v, XlError):
                    raise v
                if isinstance(v, (int, float)) and not isinstance(v, bool):      # text and blanks in the sum range are ignored
                    total += float(v)
                    count += 1
        if name in ("COUNTIFS", "COUNTIF"):
            return float(count)
        if name == "AVERAGEIFS":
            if count == 0:
                raise XlError("#DIV/0!")
            return total / count
        return total

    def match(self, args, sheet):
        val = self.scalar(self.eval_node(args[0], sheet))
        arr = self.eval_node(args[1], sheet).flat()
        mtype = int(_num(self.scalar(self.eval_node(args[2], sheet)))) if len(args) > 2 else 1
        if mtype == 0:
            for i, x in enumerate(arr):
                if _eq(x, val) or (isinstance(val, str) and isinstance(x, str) and _wild(val).match(x)):
                    return float(i + 1)
            raise XlError("#N/A")
        best = None
        for i, x in enumerate(arr):
            if isinstance(x, (int, float)) and isinstance(val, (int, float)) and ((mtype == 1 and x <= val) or (mtype == -1 and x >= val)):
                best = i
        if best is None:
            raise XlError("#N/A")
        return float(best + 1)

    def index(self, args, sheet):
        r = self.eval_node(args[0], sheet)
        row = int(_num(self.scalar(self.eval_node(args[1], sheet))))
        col = int(_num(self.scalar(self.eval_node(args[2], sheet)))) if len(args) > 2 else None
        nr, nc = r.shape
        if col is None:
            if nc == 1:
                col = 1
            elif nr == 1:
                row, col = 1, row
            else:
                raise XlError("#REF!")
        if not (1 <= row <= nr and 1 <= col <= nc):
            raise XlError("#REF!")
        return self.cell(r.sheet, r.r1 + row - 1, r.c1 + col - 1)

    def xlookup(self, args, sheet):
        val = self.scalar(self.eval_node(args[0], sheet))
        look, ret = self.eval_node(args[1], sheet), self.eval_node(args[2], sheet)
        given = lambda i: len(args) > i and args[i] != ("blank",)
        mode = int(_num(self.scalar(self.eval_node(args[4], sheet)))) if given(4) else 0
        search = int(_num(self.scalar(self.eval_node(args[5], sheet)))) if given(5) else 1
        arr = look.flat()
        for i in (range(len(arr)) if search >= 0 else range(len(arr) - 1, -1, -1)):
            x = arr[i]
            if _eq(x, val) if mode == 0 else bool(isinstance(val, str) and isinstance(x, str) and _wild(val).match(x)):
                return self.cell(ret.sheet, ret.r1 + i, ret.c1) if ret.shape[1] == 1 else self.cell(ret.sheet, ret.r1, ret.c1 + i)
        if given(3):
            return self.eval_node(args[3], sheet)
        raise XlError("#N/A")

    def vlookup(self, args, sheet):
        val = self.scalar(self.eval_node(args[0], sheet))
        tab = self.eval_node(args[1], sheet)
        col = int(_num(self.scalar(self.eval_node(args[2], sheet))))
        approx = True if len(args) < 4 else bool(self.scalar(self.eval_node(args[3], sheet)))
        keys = [row[0] for row in tab.rows()]
        if not approx:
            for i, x in enumerate(keys):
                if _eq(x, val):
                    return self.cell(tab.sheet, tab.r1 + i, tab.c1 + col - 1)
            raise XlError("#N/A")
        best = None
        for i, x in enumerate(keys):                         # approximate match: the last key <= value (assumes sorted keys)
            if isinstance(x, (int, float)) and isinstance(val, (int, float)) and x <= val:
                best = i
        if best is None:
            raise XlError("#N/A")
        return self.cell(tab.sheet, tab.r1 + best, tab.c1 + col - 1)




# ---------------------------------------------------------------- test world for the report project
def make_data(seed=4, n=300, n_products=12):
    rng = np.random.default_rng(seed)
    cats = ["Kitchen", "Living", "Bedroom", "Outdoor"]
    products = pd.DataFrame({"code": [f"P{i:02d}" for i in range(1, n_products + 1)], "product": [f"Item {i}" for i in range(1, n_products + 1)],
                             "category": [cats[i % 4] for i in range(n_products)], "unit_cost": rng.uniform(8, 60, n_products).round(2)})
    pi = rng.integers(0, n_products, n)
    orders = pd.DataFrame({
        "order_id": [f"O{i:05d}" for i in range(1, n + 1)],
        "order_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 366, n), unit="D"),
        "region": rng.choice(["North", "South", "East", "West"], n),
        "product_code": products["code"].to_numpy()[pi], "units": rng.integers(1, 13, n),
        "unit_price": (products["unit_cost"].to_numpy()[pi] * rng.uniform(1.4, 2.2, n)).round(2),
        "discount": rng.choice([0, 0, 0, .05, .1, .15, .2], n)})
    return orders, products


def truth(orders, products):
    d = orders.merge(products[["code", "category", "unit_cost"]], left_on="product_code", right_on="code", how="left", validate="m:1")
    d["revenue"] = d["units"] * d["unit_price"] * (1 - d["discount"])
    d["cost"] = d["units"] * d["unit_cost"]
    d["margin"] = d["revenue"] - d["cost"]
    return d


def verify_report(wb, orders, products, target=0.40, tol=1e-6):
    """Compare the Summary sheet with pandas through the evaluator; returns a list of problems."""
    bk = Book(wb)
    d = truth(orders, products)
    problems = []

    def check(label, got, expected):
        if isinstance(got, XlError):
            problems.append(f"{label}: Excel gives the error {got.code}")
        elif isinstance(expected, str):
            if got != expected:
                problems.append(f"{label}: Excel {got!r}, expected {expected!r}")
        elif not abs(got - expected) <= tol * max(1.0, abs(expected)):
            problems.append(f"{label}: Excel {got:,.4f}, pandas {expected:,.4f}")

    rev, mar = float(d["revenue"].sum()), float(d["margin"].sum())
    check("Summary!B3 revenue", bk.value("Summary", "B3"), rev)
    check("Summary!B4 gross margin", bk.value("Summary", "B4"), mar)
    check("Summary!B5 gross margin %", bk.value("Summary", "B5"), mar / rev)
    check("Summary!B6 status", bk.value("Summary", "B6"), "on target" if mar / rev >= target else "below target")
    regions, cats = sorted(orders["region"].unique()), sorted(products["category"].unique())
    grid = d.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum").reindex(index=regions, columns=cats).fillna(0.0)
    for i, reg in enumerate(regions):
        for j, cat in enumerate(cats):
            check(f"grid {reg}/{cat}", bk.value("Summary", f"{get_column_letter(2 + j)}{9 + i}"), float(grid.loc[reg, cat]))
    for row in wb["Summary"].iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("=") and isinstance(bk.value("Summary", c.coordinate), XlError):
                problems.append(f"error value in Summary!{c.coordinate}")
    return problems


def lint_workbook(wb, n_orders):
    """Mechanical rules for a generated workbook; returns a list of issues."""
    issues = []
    if wb.sheetnames != ["Summary", "Orders", "Products", "Inputs"]:
        issues.append(f"sheets should be Summary, Orders, Products, Inputs; found {wb.sheetnames}")
    for name in ("Orders", "Products"):
        if name in wb.sheetnames and wb[name].freeze_panes != "A2":
            issues.append(f"{name}: header row is not frozen")
    for nm in ("Order_Date", "Region", "Units", "Category", "Rev", "Cost", "Margin"):
        ref_ = wb.defined_names[nm].attr_text if nm in wb.defined_names else None
        if ref_ is None:
            issues.append(f"defined name {nm} is missing")
        elif not ref_.endswith(f"${n_orders + 1}"):
            issues.append(f"defined name {nm} ends at {ref_.split('$')[-1]} but the data end at row {n_orders + 1}: the name is stale")
    if "Target_Margin" not in wb.defined_names:
        issues.append("defined name Target_Margin is missing")
    for row in wb["Summary"].iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("="):
                f = re.sub(r'"[^"]*"', "", c.value)
                f = re.sub(r"\$?[A-Z]{1,3}\$?\d+", "", f)
                for num in re.findall(r"(?<![A-Za-z_])\d+\.?\d*", f):
                    issues.append(f"Summary!{c.coordinate}: the constant {num} is typed inside a formula (put it in a labelled cell)")
    if not wb["Summary"].conditional_formatting:
        issues.append("no conditional formatting on the Summary")
    if not wb.calculation.fullCalcOnLoad:
        issues.append("the workbook is not set to recalculate on open")
    return issues
