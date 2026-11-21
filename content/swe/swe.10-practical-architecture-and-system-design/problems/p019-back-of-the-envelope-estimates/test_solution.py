import pytest

from solution import estimate


def test_the_taskboard_example():
    assert estimate(20_000, 4, 9, 1_000, 3, 3) == {
        "avg_write_qps": 0.93, "peak_write_qps": 2.78, "avg_read_qps": 8.33, "peak_read_qps": 25.0, "storage_gb": 87.6}, \
        "20,000 users x 4 writes = 80,000 writes a day = 0.93 per second; reads are 9x that; storage is 80,000 x 365 x 3 x 1,000 bytes."


def test_the_school_app_of_the_chapter():
    got = estimate(3_000, 5, 4, 1_000, 3, 3)
    assert got["avg_write_qps"] == 0.17 and got["avg_read_qps"] == 0.69 and got["peak_read_qps"] == 2.08, \
        f"3,000 users x 5 actions: 15,000 writes/day (0.17/s) and 60,000 reads/day (0.69/s, about 2/s at a 3x peak); got {got}"


def test_a_big_product_changes_the_answer():
    got = estimate(10_000_000, 3, 49, 2_000, 3, 3)
    assert got["avg_write_qps"] == 347.22 and got["peak_read_qps"] == 51041.67, f"A social feed at 10 million users: thousands of reads per second; got {got}"
    assert got["storage_gb"] == 65700.0, f"65.7 TB after 3 years; got {got['storage_gb']}"


def test_the_peak_uses_the_unrounded_average():
    got = estimate(100_000, 1, 1, 1, 1, 3)
    assert got["avg_write_qps"] == 1.16 and got["peak_write_qps"] == 3.47, \
        "1.1574 x 3 = 3.4722 -> 3.47. Rounding the average first (1.16 x 3 = 3.48) gives a different answer: round only at the end."


def test_reads_per_write_scales_the_reads_only():
    low, high = estimate(864_000, 10, 1, 100, 1, 2), estimate(864_000, 10, 100, 100, 1, 2)
    assert low["avg_write_qps"] == high["avg_write_qps"] == 100.0, "864,000 users x 10 writes = exactly 100 writes per second."
    assert low["storage_gb"] == high["storage_gb"]
    assert (low["avg_read_qps"], high["avg_read_qps"]) == (100.0, 10_000.0), "Reads are writes x reads_per_write."


def test_zero_users_is_zero_load():
    assert estimate(0, 5, 5, 1_000, 3, 3) == {"avg_write_qps": 0.0, "peak_write_qps": 0.0, "avg_read_qps": 0.0, "peak_read_qps": 0.0, "storage_gb": 0.0}


def test_peak_factor_of_one_is_allowed():
    got = estimate(86_400, 1, 1, 1, 1, 1)
    assert got["avg_write_qps"] == 1.0 and got["peak_write_qps"] == 1.0, "One write per user per day for 86,400 users is exactly 1 per second."


@pytest.mark.parametrize("args", [(-1, 1, 1, 1, 1, 1), (1, -1, 1, 1, 1, 1), (1, 1, -1, 1, 1, 1), (1, 1, 1, -1, 1, 1),
                                  (1, 1, 1, 1, 0, 1), (1, 1, 1, 1, -2, 1), (1, 1, 1, 1, 1, 0.5)])
def test_bad_input(args):
    with pytest.raises(ValueError):
        estimate(*args)


def test_the_result_has_exactly_the_documented_keys():
    assert set(estimate(1, 1, 1, 1, 1, 1)) == {"avg_write_qps", "peak_write_qps", "avg_read_qps", "peak_read_qps", "storage_gb"}
