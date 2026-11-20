def uses_index(db, sql, params=()):
    rows = db.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return any("SEARCH" in row[3] for row in rows)
