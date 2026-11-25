import json

import pandas as pd


def _field(text):
    table, col = text[:-1].split("[")
    return table, col


def model_from_project(folder, Model):
    spec = json.loads((folder / "model_spec.json").read_text(encoding="utf-8"))
    m = Model()
    for name, t in spec["tables"].items():
        path = folder / t["file"]
        m.table(name, pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path))
    for r in spec["relationships"]:
        many, mcol = _field(r["from"])
        one, ocol = _field(r["to"])
        try:
            m.relate(many, mcol, one, ocol, active=r.get("active", True), both=(r.get("direction") == "both"))
        except Exception as e:
            raise ValueError(f"relationship {r['from']} -> {r['to']}: {e}") from None
    for meas in spec["measures"]:
        m.measure(meas["name"], meas["dax"])
    return m, spec


def check_report_spec(report, model, spec):
    problems = []
    names = {m["name"] for m in spec["measures"]}
    exists = lambda f: _field(f)[0] in model.t and _field(f)[1] in model.t[_field(f)[0]].columns
    for page, p in report.items():
        for f in p.get("slicers", []):
            if not exists(f):
                problems.append(f"{page}: slicer field {f} does not exist")
        for v in p["visuals"]:
            ms = v.get("measures", v.get("measure", []))
            for name in [ms] if isinstance(ms, str) else ms:
                if name not in names:
                    problems.append(f"{page}: measure [{name}] does not exist")
            for key in ("axis", "rows", "columns"):
                if key in v and not exists(v[key]):
                    problems.append(f"{page}: field {v[key]} does not exist")
    return problems
