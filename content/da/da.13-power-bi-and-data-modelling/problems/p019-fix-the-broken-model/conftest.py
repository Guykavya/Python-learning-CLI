import re
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP


class DaxError(Exception):
    pass


TOK = re.compile(r"""\s*(?:
  (?P<str>"(?:[^"]|"")*")|
  (?P<num>\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+)|
  (?P<col>(?:'[^']+'|[A-Za-z_][\w]*)\[[^\]]+\])|
  (?P<meas>\[[^\]]+\])|
  (?P<kw>\b(?:VAR|RETURN|IN|TRUE|FALSE)\b)|
  (?P<func>[A-Za-z_][\w.]*(?=\())|
  (?P<name>[A-Za-z_][\w]*)|
  (?P<op>&&|\|\||<>|<=|>=|[-+*/=<>(){},])
)""", re.X | re.I)


def tokenize(s):
    pos, out = 0, []
    while pos < len(s):
        m = TOK.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip() == "":
                break
            raise DaxError(f"cannot read the formula near: {s[pos:pos + 20]!r}")
        pos = m.end()
        out.append((m.lastgroup, m.group(m.lastgroup)))
    return out


class P:
    def __init__(self, text):
        self.t, self.i = tokenize(text), 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        n = self.expr()
        if self.i != len(self.t):
            raise DaxError("unexpected text after the end of the expression")
        return n

    def expr(self):
        binds = []
        while self.peek() == ("kw", "VAR") or (self.peek()[0] == "kw" and self.peek()[1].upper() == "VAR"):
            self.take()
            name = self.take()[1]
            self.take()                                    # =
            binds.append((name, self.orx()))
        if binds:
            if not (self.peek()[0] == "kw" and self.peek()[1].upper() == "RETURN"):
                raise DaxError("VAR without RETURN")
            self.take()
            return ("let", binds, self.expr())
        return self.orx()

    def orx(self):
        n = self.andx()
        while self.peek() == ("op", "||"):
            self.take(); n = ("bin", "||", n, self.andx())
        return n

    def andx(self):
        n = self.cmpx()
        while self.peek() == ("op", "&&"):
            self.take(); n = ("bin", "&&", n, self.cmpx())
        return n

    def cmpx(self):
        n = self.add()
        k, v = self.peek()
        if k == "op" and v in ("=", "<>", "<", ">", "<=", ">="):
            self.take(); return ("bin", v, n, self.add())
        if k == "kw" and v.upper() == "IN":
            self.take(); return ("bin", "IN", n, self.add())
        return n

    def add(self):
        n = self.mul()
        while self.peek()[0] == "op" and self.peek()[1] in ("+", "-"):
            op = self.take()[1]; n = ("bin", op, n, self.mul())
        return n

    def mul(self):
        n = self.unary()
        while self.peek()[0] == "op" and self.peek()[1] in ("*", "/"):
            op = self.take()[1]; n = ("bin", op, n, self.unary())
        return n

    def unary(self):
        if self.peek() == ("op", "-"):
            self.take(); return ("neg", self.unary())
        return self.prim()

    def prim(self):
        k, v = self.take()
        if k == "num": return ("num", float(v))
        if k == "str": return ("str", v[1:-1].replace('""', '"'))
        if k == "kw" and v.upper() in ("TRUE", "FALSE"): return ("bool", v.upper() == "TRUE")
        if k == "col":
            t, c = v.rsplit("[", 1)
            return ("col", t.strip("'"), c[:-1])
        if k == "meas": return ("meas", v[1:-1])
        if k == "name": return ("var", v)
        if k == "func":
            self.take()
            args = []
            if self.peek() != ("op", ")"):
                while True:
                    args.append(self.expr())
                    if self.peek() == ("op", ","):
                        self.take(); continue
                    break
            if self.take() != ("op", ")"): raise DaxError("missing )")
            return ("call", v.upper(), args)
        if (k, v) == ("op", "("):
            n = self.expr()
            if self.take() != ("op", ")"): raise DaxError("missing )")
            return n
        if (k, v) == ("op", "{"):
            items = []
            while True:
                items.append(self.expr())
                if self.peek() == ("op", ","):
                    self.take(); continue
                break
            if self.take() != ("op", "}"): raise DaxError("missing }")
            return ("list", items)
        raise DaxError(f"unexpected {v!r}")


class Rel:
    def __init__(self, many, mcol, one, ocol, active=True, both=False):
        self.many, self.mcol, self.one, self.ocol, self.active, self.both = many, mcol, one, ocol, active, both

    def key(self):
        return (self.many, self.mcol, self.one, self.ocol)


class Tab:
    """A table value: a table name and a boolean mask of its rows (plus optional extra columns for iterators)."""
    def __init__(self, name, mask):
        self.name, self.mask = name, mask


class Ctx:
    def __init__(self, cols=None, rows=None, active=None):
        self.cols = dict(cols or {})            # (table, column) -> set of allowed values
        self.rows = dict(rows or {})            # table -> boolean mask (from FILTER or time intelligence)
        self.active = active                    # None = the model's active relationships; else a set of relationship keys
        self.vars = {}

    def copy(self):
        c = Ctx(self.cols, self.rows, self.active)
        c.vars = dict(self.vars)
        return c


class Model:
    """A small semantic model and a DAX-subset evaluator. It exists to test measures offline; Power BI is the final authority."""
    def __init__(self):
        self.t, self.rels, self.measures = {}, [], {}

    def table(self, name, df):
        self.t[name] = df.reset_index(drop=True)
        return self

    def relate(self, many, mcol, one, ocol, active=True, both=False):
        if not self.t[one][ocol].is_unique:
            raise DaxError(f"{one}[{ocol}] must be unique: it is the 'one' side of a relationship")
        self.rels.append(Rel(many, mcol, one, ocol, active, both))
        return self

    def measure(self, name, expr):
        self.measures[name] = expr
        return self

    # ---- filter propagation
    def _active_rels(self, ctx):
        if ctx.active is None:
            return [r for r in self.rels if r.active]
        return [r for r in self.rels if r.key() in ctx.active]

    def visible(self, table, ctx, _seen=None):
        seen = _seen or {table}
        df = self.t[table]
        mask = np.ones(len(df), bool)
        for (t, c), vals in ctx.cols.items():
            if t == table:
                mask &= df[c].isin(vals).to_numpy()
        if table in ctx.rows:
            mask &= ctx.rows[table]
        for r in self._active_rels(ctx):
            if r.many == table and r.one not in seen:                       # filters flow from the one side to the many side
                other = self.visible(r.one, ctx, seen | {table})
                if other.all() and not self._has_filter(r.one, ctx, seen | {table}):
                    continue
                keys = self.t[r.one].loc[other, r.ocol]
                mask &= df[r.mcol].isin(keys).to_numpy()
            elif r.one == table and r.both and r.many not in seen:          # bidirectional: the many side filters the one side
                other = self.visible(r.many, ctx, seen | {table})
                if other.all() and not self._has_filter(r.many, ctx, seen | {table}):
                    continue
                keys = self.t[r.many].loc[other, r.mcol]
                mask &= df[r.ocol].isin(keys).to_numpy()
        return mask

    def _has_filter(self, table, ctx, seen):
        if any(t == table for (t, _) in ctx.cols) or table in ctx.rows:
            return True
        for r in self._active_rels(ctx):
            if r.many == table and r.one not in seen and self._has_filter(r.one, ctx, seen | {table}):
                return True
            if r.one == table and r.both and r.many not in seen and self._has_filter(r.many, ctx, seen | {table}):
                return True
        return False

    # ---- evaluation
    def evaluate(self, expr, filters=None, ctx=None):
        """Evaluate a measure name or a DAX expression. `filters` maps 'Table[Column]' to a list of allowed values (like slicers)."""
        c = ctx.copy() if ctx else Ctx()
        for key, vals in (filters or {}).items():
            t, col = key.split("[")
            c.cols[(t.strip("'"), col[:-1])] = set(vals if isinstance(vals, (list, tuple, set)) else [vals])
        text = self.measures.get(expr, expr)
        v = self.ev(P(text).parse(), c, None)
        if isinstance(v, Tab):
            raise DaxError("a measure must return a single value, not a table")
        return v

    def ev(self, n, ctx, row):
        k = n[0]
        if k == "num": return n[1]
        if k == "str": return n[1]
        if k == "bool": return n[1]
        if k == "var":
            if n[1] in ctx.vars: return ctx.vars[n[1]]
            raise DaxError(f"unknown name {n[1]}")
        if k == "let":
            c = ctx.copy()
            for name, e in n[1]:
                c.vars[name] = self.ev(e, c, row)
            return self.ev(n[2], c, row)
        if k == "neg":
            v = self.ev(n[1], ctx, row)
            return None if v is None else -v
        if k == "meas":
            if n[1] not in self.measures: raise DaxError(f"unknown measure [{n[1]}]")
            return self.ev(P(self.measures[n[1]]).parse(), ctx, None)
        if k == "col":
            return self.column(n[1], n[2], ctx, row)
        if k == "list":
            return [self.ev(i, ctx, row) for i in n[1]]
        if k == "bin":
            return self.binop(n[1], self.ev(n[2], ctx, row), self.ev(n[3], ctx, row))
        if k == "call":
            return self.call(n[1], n[2], ctx, row)
        raise DaxError("cannot evaluate")

    def column(self, table, col, ctx, row):
        if table not in self.t or col not in self.t[table].columns:
            raise DaxError(f"unknown column {table}[{col}]")
        if row is not None and row[0] == table:                       # inside an iterator over this table: one value per row
            return self.t[table][col][row[1]].reset_index(drop=True)
        raise DaxError(f"{table}[{col}] cannot be used here without an aggregation (a column needs a row context)")

    def binop(self, op, a, b):
        if op == "IN":
            return a.isin(b) if isinstance(a, pd.Series) else a in b
        if isinstance(a, (pd.Series, np.ndarray)) or isinstance(b, (pd.Series, np.ndarray)):
            a = a.fillna(0) if isinstance(a, pd.Series) else a
            b = b.fillna(0) if isinstance(b, pd.Series) else b
            return {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b, "=": lambda: a == b, "<>": lambda: a != b,
                    "<": lambda: a < b, ">": lambda: a > b, "<=": lambda: a <= b, ">=": lambda: a >= b, "&&": lambda: a & b, "||": lambda: a | b}[op]()
        if op in ("&&", "||"):
            return (bool(a) and bool(b)) if op == "&&" else (bool(a) or bool(b))
        if op in ("+", "-"):                                           # BLANK behaves as 0 in + and -
            a, b = 0 if a is None else a, 0 if b is None else b
            return a + b if op == "+" else a - b
        if op in ("*", "/"):
            if a is None or b is None: return None
            if op == "/":
                if a is None: return None
                if b is None or b == 0: return float("nan") if a == 0 else float("inf")      # DAX gives Infinity or NaN, not an error
                return a / b
            return a * b
        a, b = (0 if a is None and not isinstance(b, str) else a), (0 if b is None and not isinstance(a, str) else b)
        return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]

    # ---- table expressions
    def as_tab(self, node, ctx, row):
        if node[0] == "var" and isinstance(ctx.vars.get(node[1]), Tab):
            return ctx.vars[node[1]]
        if node[0] == "var" and node[1] in self.t:
            return Tab(node[1], self.visible(node[1], ctx))
        if node[0] == "call" and node[1] == "FILTER":
            return self.call("FILTER", node[2], ctx, row)
        if node[0] == "call" and node[1] == "ALL":
            return self.call("ALL", node[2], ctx, row)
        raise DaxError("a table is expected here")

    def call(self, name, args, ctx, row):
        ev = lambda i: self.ev(args[i], ctx, row)
        if name == "CALCULATE":
            c = ctx.copy()
            for a in args[1:]:
                self.apply_filter(a, c, row)
            return self.ev(args[0], c, row)
        if name in ("SUM", "AVERAGE", "MIN", "MAX", "COUNT", "DISTINCTCOUNT"):
            t, col = args[0][1], args[0][2]
            s = self.t[t].loc[self.visible(t, ctx), col]
            if name == "DISTINCTCOUNT": return float(s.nunique()) or None
            if name == "COUNT": return float(s.notna().sum()) or None
            s = pd.to_numeric(s, errors="coerce").dropna()
            if len(s) == 0: return None
            return float({"SUM": s.sum, "AVERAGE": s.mean, "MIN": s.min, "MAX": s.max}[name]())
        if name == "COUNTROWS":
            tab = self.as_tab(args[0], ctx, row)
            return float(tab.mask.sum()) or None
        if name in ("SUMX", "AVERAGEX"):
            tab = self.as_tab(args[0], ctx, row)
            idx = pd.Series(tab.mask)
            vals = self.ev(args[1], ctx, (tab.name, idx))
            vals = vals if isinstance(vals, pd.Series) else pd.Series([vals] * int(tab.mask.sum()))
            vals = vals.dropna()
            if len(vals) == 0: return None
            return float(vals.sum() if name == "SUMX" else vals.mean())
        if name == "RELATED":
            t, col = args[0][1], args[0][2]
            if row is None: raise DaxError("RELATED needs a row context")
            base, idx = row
            rel = next((r for r in self._active_rels(ctx) if r.many == base and r.one == t), None)
            if rel is None: raise DaxError(f"no active relationship from {base} to {t}")
            keyed = self.t[t].set_index(rel.ocol)[col]
            return self.t[base].loc[idx.to_numpy(), rel.mcol].map(keyed).reset_index(drop=True)
        if name == "DIVIDE":
            a, b = ev(0), ev(1)
            alt = ev(2) if len(args) > 2 else None
            if a is None or b is None or b == 0: return alt
            return a / b
        if name == "IF":
            c = ev(0)
            return ev(1) if c else (ev(2) if len(args) > 2 else None)
        if name == "ISBLANK": return ev(0) is None
        if name == "BLANK": return None
        if name == "COALESCE":
            for i in range(len(args)):
                v = ev(i)
                if v is not None: return v
            return None
        if name == "ROUND": return None if ev(0) is None else float(Decimal_round(ev(0), int(ev(1))))
        if name == "ABS": return None if ev(0) is None else abs(ev(0))
        if name == "HASONEVALUE": return len(self.values(args[0], ctx)) == 1
        if name == "SELECTEDVALUE":
            vals = self.values(args[0], ctx)
            return vals[0] if len(vals) == 1 else (ev(1) if len(args) > 1 else None)
        if name == "VALUES": return self.values(args[0], ctx)
        if name == "FILTER":
            tab = self.as_tab(args[0], ctx, row)
            cond = self.ev(args[1], ctx, (tab.name, pd.Series(tab.mask)))
            full = np.zeros(len(self.t[tab.name]), bool)
            full[np.flatnonzero(tab.mask)] = np.asarray(cond, bool)
            return Tab(tab.name, full)
        if name == "ALL":
            a = args[0]
            if a[0] == "var" and a[1] in self.t:
                return Tab(a[1], np.ones(len(self.t[a[1]]), bool))
            raise DaxError("ALL here must name a table")
        raise DaxError(f"function {name} is not available in this engine")

    def values(self, a, ctx):
        t, col = a[1], a[2]
        s = self.t[t].loc[self.visible(t, ctx), col]
        return sorted(s.dropna().unique().tolist())

    # ---- CALCULATE's filter arguments
    def apply_filter(self, a, c, row):
        k = a[0]
        if k == "bin" and a[2][0] == "col":                           # Table[Column] op value  (replaces the filter on that column)
            t, col = a[2][1], a[2][2]
            val = self.ev(a[3], c, row)
            s = self.t[t][col]
            op = a[1]
            allowed = set(s[s.isin(val)].unique()) if op == "IN" else set(s[{"=": s == val, "<>": s != val, "<": s < val, ">": s > val, "<=": s <= val, ">=": s >= val}[op]].unique())
            c.cols[(t, col)] = allowed
            return
        if k == "call":
            f = a[1]
            if f in ("ALL", "REMOVEFILTERS"):
                if not a[2]: c.cols.clear(); c.rows.clear(); return
                x = a[2][0]
                if x[0] == "var":
                    self._clear_table(x[1], c)
                elif x[0] == "col":
                    c.cols.pop((x[1], x[2]), None)
                return
            if f == "ALLEXCEPT":
                t = a[2][0][1]
                keep = {(x[1], x[2]) for x in a[2][1:]}
                for key in [k_ for k_ in c.cols if k_[0] == t and k_ not in keep]:
                    del c.cols[key]
                c.rows.pop(t, None)
                return
            if f == "FILTER":
                tab = self.call("FILTER", a[2], c, row)
                self._clear_table(tab.name, c)
                c.rows[tab.name] = tab.mask
                return
            if f == "USERELATIONSHIP":
                x, y = a[2][0], a[2][1]
                new = next((r for r in self.rels if {(r.many, r.mcol), (r.one, r.ocol)} == {(x[1], x[2]), (y[1], y[2])}), None)
                if new is None: raise DaxError("no such relationship")
                base = {r.key() for r in self._active_rels(c)}
                base = {k_ for k_ in base if not ((k_[0], k_[2]) == (new.many, new.one))}      # switch off the active one between the same tables
                base.add(new.key())
                c.active = base
                return
            if f in ("SAMEPERIODLASTYEAR", "DATESYTD", "DATEADD"):
                t, col = a[2][0][1], a[2][0][2]
                vis = self.t[t].loc[self.visible(t, c), col]
                allv = self.t[t][col]
                if f == "SAMEPERIODLASTYEAR":
                    shifted = vis + pd.DateOffset(years=-1)
                    allowed = set(allv[allv.isin(shifted)])
                elif f == "DATESYTD":
                    if len(vis) == 0: allowed = set()
                    else:
                        last = vis.max()
                        allowed = set(allv[(allv.dt.year == last.year) & (allv <= last)])
                else:
                    n, unit = int(self.ev(a[2][1], c, row)), a[2][2][1].upper() if a[2][2][0] == "var" else str(a[2][2][1]).upper()
                    off = {"DAY": pd.DateOffset(days=n), "MONTH": pd.DateOffset(months=n), "YEAR": pd.DateOffset(years=n)}[unit]
                    allowed = set(allv[allv.isin(vis + off)])
                self._clear_table(t, c)
                c.cols[(t, col)] = allowed
                return
        raise DaxError("this kind of filter argument is not available in this engine")

    def _clear_table(self, t, c):
        for key in [k_ for k_ in c.cols if k_[0] == t]:
            del c.cols[key]
        c.rows.pop(t, None)

    # ---- a visual: group by columns, evaluate measures
    def query(self, group_by, measures, filters=None):
        """Like a matrix or table visual: one row per combination of the group-by columns that exists in the model."""
        cols = []
        for g in group_by:
            t, c = g.split("[")
            cols.append((t.strip("'"), c[:-1]))
        base = Ctx()
        for key, vals in (filters or {}).items():
            t, col = key.split("[")
            base.cols[(t.strip("'"), col[:-1])] = set(vals if isinstance(vals, (list, tuple, set)) else [vals])
        # the combinations that exist (in the dimension tables) under the slicer filters
        frames = []
        for t, c in cols:
            vis = self.t[t].loc[self.visible(t, base), c].dropna().unique()
            frames.append(pd.DataFrame({f"{t}[{c}]": sorted(vis.tolist())}))
        grid = frames[0]
        for f in frames[1:]:
            grid = grid.merge(f, how="cross")
        rows = []
        for rec in grid.to_dict("records"):
            ctx = base.copy()
            for (t, c), key in zip(cols, grid.columns):
                ctx.cols[(t, c)] = {rec[key]}
            out = dict(rec)
            vals = [self.ev(P(self.measures.get(m, m)).parse(), ctx, None) for m in measures]
            if all(v is None for v in vals):
                continue                                              # like a visual, hide rows where every measure is blank
            out.update(dict(zip(measures, vals)))
            rows.append(out)
        return pd.DataFrame(rows)


def Decimal_round(x, n):
    return Decimal(format(float(x), ".15g")).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP)




# ---------------------------------------------------------------- a small BrightMart-like star for the tests
import json


def make_mini(seed=3, n_orders=120):
    rng = np.random.default_rng(seed)
    d = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    date = pd.DataFrame({"DateKey": d.strftime("%Y%m%d").astype(int), "Date": d, "Year": d.year, "Quarter": "Q" + d.quarter.astype(str),
                         "MonthNum": d.month, "MonthName": d.strftime("%b"), "YearMonth": d.strftime("%Y-%m"), "MonthStart": d.to_period("M").to_timestamp()})
    cats = ["Kitchen", "Living", "Bedroom", "Outdoor"]
    product = pd.DataFrame({"ProductKey": np.arange(1, 13), "Product": [f"Product {i:02d}" for i in range(1, 13)],
                            "Category": [cats[i % 4] for i in range(12)], "UnitCost": rng.uniform(6, 55, 12).round(2)})
    product["ListPrice"] = (product["UnitCost"] * rng.uniform(1.4, 2.3, 12)).round(2)
    customer = pd.DataFrame({"CustomerKey": np.arange(1, 31), "Customer": [f"Customer {i:02d}" for i in range(1, 31)],
                             "Segment": rng.choice(["Consumer", "Small business", "Corporate"], 30)})
    store = pd.DataFrame({"StoreKey": np.arange(1, 7), "Store": [f"Store {i:02d}" for i in range(1, 7)],
                          "Region": ["North", "North", "South", "South", "East", "Online"]})
    od = d[d < "2025-01-01"][rng.integers(0, 731, n_orders)]
    orders = pd.DataFrame({"OrderID": [f"O{i:04d}" for i in range(1, n_orders + 1)], "OrderDate": od, "CustomerKey": rng.integers(1, 31, n_orders),
                           "StoreKey": rng.integers(1, 7, n_orders), "Freight": rng.uniform(3, 25, n_orders).round(2)})
    k = rng.integers(1, 4, n_orders)
    idx = np.repeat(np.arange(n_orders), k)
    sales = pd.DataFrame({"OrderID": orders["OrderID"].to_numpy()[idx], "LineNo": np.concatenate([np.arange(1, x + 1) for x in k]),
                          "OrderDate": od[idx], "CustomerKey": orders["CustomerKey"].to_numpy()[idx], "StoreKey": orders["StoreKey"].to_numpy()[idx]})
    sales["ShipDate"] = sales["OrderDate"] + pd.to_timedelta(rng.integers(1, 8, len(sales)), unit="D")
    sales["ProductKey"] = rng.integers(1, 13, len(sales))
    sales["Quantity"] = rng.integers(1, 7, len(sales))
    sales["UnitPrice"] = (product["ListPrice"].to_numpy()[sales["ProductKey"].to_numpy() - 1] * rng.uniform(.95, 1.05, len(sales))).round(2)
    sales["DiscountPct"] = rng.choice([0, 0, 0, .05, .1, .15], len(sales))
    sales["OrderDateKey"] = sales["OrderDate"].dt.strftime("%Y%m%d").astype(int)
    sales["ShipDateKey"] = sales["ShipDate"].dt.strftime("%Y%m%d").astype(int)
    sales = sales[["OrderID", "LineNo", "OrderDateKey", "ShipDateKey", "CustomerKey", "ProductKey", "StoreKey", "Quantity", "UnitPrice", "DiscountPct"]]
    orders = orders.assign(OrderDateKey=orders["OrderDate"].dt.strftime("%Y%m%d").astype(int))[["OrderID", "OrderDateKey", "CustomerKey", "StoreKey", "Freight"]]
    return {"Date": date, "Product": product, "Customer": customer, "Store": store, "Sales": sales, "Orders": orders}


def build_model(tables, both=()):
    m = Model()
    for name in ("Date", "Product", "Customer", "Store", "Sales", "Orders"):
        m.table(name, tables[name])
    m.relate("Sales", "OrderDateKey", "Date", "DateKey", both="Sales-Date" in both)
    m.relate("Sales", "ShipDateKey", "Date", "DateKey", active=False)
    m.relate("Sales", "ProductKey", "Product", "ProductKey", both="Sales-Product" in both)
    m.relate("Sales", "CustomerKey", "Customer", "CustomerKey", both="Sales-Customer" in both)
    m.relate("Sales", "StoreKey", "Store", "StoreKey", both="Sales-Store" in both)
    m.relate("Orders", "OrderDateKey", "Date", "DateKey")
    m.relate("Orders", "CustomerKey", "Customer", "CustomerKey")
    m.relate("Orders", "StoreKey", "Store", "StoreKey")
    return m


REVENUE = "SUMX(Sales, Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct]))"


def flat_of(tables):
    s = tables["Sales"].merge(tables["Product"], on="ProductKey", validate="m:1").merge(
        tables["Store"].rename(columns={"Region": "StoreRegion"}), on="StoreKey", validate="m:1")
    s["Revenue"] = s["Quantity"] * s["UnitPrice"] * (1 - s["DiscountPct"])
    s["Cost"] = s["Quantity"] * s["UnitCost"]
    s["Year"] = s["OrderDateKey"] // 10000
    s["Month"] = (s["OrderDateKey"] // 100) % 100
    return s
