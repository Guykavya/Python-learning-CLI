import pytest

from solution import worker_plan


def test_sync_uses_two_cores_plus_one():
    assert worker_plan(4, "sync", 2048, 150) == {"server": "gunicorn", "workers": 9, "threads": 1, "concurrent": 9}, \
        "A sync plan on 4 cores with plenty of memory is 2 * 4 + 1 = 9 workers, 1 thread each, 9 requests in flight."


def test_threaded_multiplies_by_four_threads():
    plan = worker_plan(4, "threaded", 2048, 150)
    assert plan == {"server": "gunicorn", "workers": 9, "threads": 4, "concurrent": 36}, \
        f"gthread: the same 9 workers with threads=4 give 36 requests in flight (the chapter's 'Try it'); got {plan}"


def test_memory_caps_the_workers():
    assert worker_plan(8, "sync", 1024, 300)["workers"] == 3, \
        "2 * 8 + 1 = 17 workers would need 5100 MB; with 1024 MB and 300 MB per worker only 3 fit (use integer division)."
    assert worker_plan(8, "threaded", 1024, 300) == {"server": "gunicorn", "workers": 3, "threads": 4, "concurrent": 12}


def test_async_is_one_process_per_core():
    assert worker_plan(4, "async", 4096, 200) == {"server": "uvicorn", "workers": 4, "threads": None, "concurrent": None}, \
        "Async apps: server 'uvicorn', workers = cpus (capped by memory), threads and concurrent are None."
    assert worker_plan(16, "async", 600, 200)["workers"] == 3, "Memory caps async workers too: 600 // 200 = 3."


def test_exactly_one_worker_fits():
    assert worker_plan(1, "sync", 200, 200)["workers"] == 1, "memory_mb == mb_per_worker is allowed: one worker."
    assert worker_plan(4, "sync", 399, 200)["workers"] == 1, "399 MB holds only one 200 MB worker."


def test_single_core():
    assert worker_plan(1, "sync", 4096, 100)["workers"] == 3, "2 * 1 + 1 = 3."


@pytest.mark.parametrize("args", [
    (0, "sync", 1024, 100),
    (4, "sync", 1024, 0),
    (4, "sync", 1024, -5),
    (4, "gevent", 1024, 100),
    (4, "sync", 99, 100),
])
def test_bad_input_raises(args):
    with pytest.raises(ValueError):
        worker_plan(*args)
