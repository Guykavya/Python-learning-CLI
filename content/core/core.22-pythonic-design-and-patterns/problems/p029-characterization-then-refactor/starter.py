def legacy_report(rows):
    out = []
    out.append("REPORT")
    depts = {}
    skipped = 0
    for r in rows:
        if r.get("status") == "void":
            continue
        else:
            if r.get("name") and str(r.get("name")).strip() != "":
                if r.get("dept") and str(r.get("dept")).strip() != "":
                    if isinstance(r.get("amount"), (int, float)) and not isinstance(r.get("amount"), bool):
                        if r["amount"] >= 0:
                            if r.get("status") == "paid" or r.get("status") == "pending":
                                d = str(r["dept"]).strip().title()
                                if d not in depts:
                                    depts[d] = {"count": 0, "paid": 0, "pending": 0, "top": None}
                                depts[d]["count"] = depts[d]["count"] + 1
                                if r["status"] == "paid":
                                    depts[d]["paid"] = depts[d]["paid"] + r["amount"]
                                else:
                                    depts[d]["pending"] = depts[d]["pending"] + r["amount"]
                                n = str(r["name"]).strip()
                                if depts[d]["top"] is None:
                                    depts[d]["top"] = (n, r["amount"])
                                else:
                                    if r["amount"] > depts[d]["top"][1]:
                                        depts[d]["top"] = (n, r["amount"])
                                    else:
                                        if r["amount"] == depts[d]["top"][1]:
                                            if n < depts[d]["top"][0]:
                                                depts[d]["top"] = (n, r["amount"])
                            else:
                                skipped = skipped + 1
                        else:
                            skipped = skipped + 1
                    else:
                        skipped = skipped + 1
                else:
                    skipped = skipped + 1
            else:
                skipped = skipped + 1
    if len(depts) == 0:
        out.append("no data")
    else:
        total_paid = 0
        total_pending = 0
        for d in sorted(depts.keys()):
            out.append("== " + d + " ==")
            out.append("  rows: " + str(depts[d]["count"]) + "  paid: " + "%.2f" % depts[d]["paid"] + "  pending: " + "%.2f" % depts[d]["pending"])
            out.append("  top: " + depts[d]["top"][0] + " (" + "%.2f" % depts[d]["top"][1] + ")")
            total_paid = total_paid + depts[d]["paid"]
            total_pending = total_pending + depts[d]["pending"]
        out.append("TOTAL paid: " + "%.2f" % total_paid + "  pending: " + "%.2f" % total_pending)
    if skipped > 0:
        out.append("SKIPPED: " + str(skipped))
    return "\n".join(out)
