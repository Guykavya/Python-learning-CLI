import pandas as pd
from solution import revenue_by_country


def make(tmp_path, parts):
    base = tmp_path / "orders"
    for country, files in parts.items():
        d = base / f"country={country}"
        d.mkdir(parents=True)
        for i, (ids, amounts) in enumerate(files):
            pd.DataFrame({"order_id": ids, "amount": amounts}).to_parquet(d / f"part-{i}.parquet", index=False)
    return str(base)


def test_two_partitions(con, tmp_path):
    folder = make(tmp_path, {"IN": [([1, 2], [499, 3999])], "US": [([3], [499])]})
    got = [tuple(r) for r in revenue_by_country(con, folder)]
    assert got == [("IN", 4498), ("US", 499)], "The country values come from the folder names (country=IN): use hive_partitioning = true and group by country."


def test_several_files_in_one_partition(con, tmp_path):
    folder = make(tmp_path, {"UK": [([1], [10]), ([2, 3], [20, 30])], "IN": [([4], [1])]})
    got = [tuple(r) for r in revenue_by_country(con, folder)]
    assert got == [("IN", 1), ("UK", 60)], "A partition folder can hold several files: use a glob that reads them all (**/*.parquet)."


def test_sorted_by_country(con, tmp_path):
    folder = make(tmp_path, {"US": [([1], [5])], "IN": [([2], [6])], "DE": [([3], [7])]})
    assert [r[0] for r in revenue_by_country(con, folder)] == ["DE", "IN", "US"], "Sort the result by country."


def test_uses_hive_partitioning(con, tmp_path):
    class Spy:
        def __init__(self, c):
            self._c, self.log = c, []

        def execute(self, sql, *a, **k):
            self.log.append(str(sql))
            return self._c.execute(sql, *a, **k)

        def sql(self, sql, *a, **k):
            self.log.append(str(sql))
            return self._c.sql(sql, *a, **k)

        def __getattr__(self, n):
            return getattr(self._c, n)

    folder = make(tmp_path, {"IN": [([1], [5])]})
    spy = Spy(con)
    revenue_by_country(spy, folder)
    assert "hive_partitioning" in " ".join(spy.log).lower(), "Use the read_parquet option hive_partitioning = true."
