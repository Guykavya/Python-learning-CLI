import asyncio
import time

import httpx
import pytest

from solution import download_all, file_name

SITE = "https://files.test"


# ---------------------------------------------------------------- a fake file server

def ok(data, delay=0.0):
    """Answer 200 with `data` after `delay` seconds."""
    async def answer(server, request):
        await asyncio.sleep(delay)
        return httpx.Response(200, content=data)
    return answer


def status(code):
    async def answer(server, request):
        return httpx.Response(code, text=f"status {code}")
    return answer


def network_error(exc_class):
    async def answer(server, request):
        raise exc_class("simulated network problem", request=request)
    return answer


def slow(seconds):
    """The server takes `seconds` before even answering."""
    async def answer(server, request):
        await asyncio.sleep(seconds)
        return httpx.Response(200, content=b"too late")
    return answer


def broken_stream(first, exc_class=httpx.ReadError):
    """200, sends `first`, then the connection breaks."""
    async def answer(server, request):
        async def body():
            yield first
            await asyncio.sleep(0.01)
            raise exc_class("connection lost mid-body")
        return httpx.Response(200, content=body())
    return answer


def paused_stream(first, rest, wait_seconds=10.0):
    """200, sends `first`, then waits (until server.resume is set, or wait_seconds)."""
    async def answer(server, request):
        async def body():
            yield first
            server.reached += 1                 # the first chunk has been taken by the client
            try:
                async with asyncio.timeout(wait_seconds):
                    await server.resume.wait()
            except TimeoutError:
                pass
            yield rest
        return httpx.Response(200, content=body())
    return answer


class FakeServer:
    def __init__(self, routes):
        self.routes = routes            # path -> list of answers, one per attempt
        self.calls = {}
        self.in_flight = 0
        self.peak = 0
        self.reached = 0
        self.resume = asyncio.Event()

    async def handler(self, request):
        path = request.url.path
        attempt = self.calls.get(path, 0)
        self.calls[path] = attempt + 1
        answers = self.routes[path]
        answer = answers[min(attempt, len(answers) - 1)]
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        try:
            return await answer(self, request)
        finally:
            self.in_flight -= 1


class FakeSleep:
    def __init__(self):
        self.delays = []

    async def __call__(self, seconds):
        self.delays.append(seconds)
        await asyncio.sleep(0)


def url(name):
    return f"{SITE}/{name}"


def download(routes, urls, dest, **kwargs):
    """Run download_all against a fake server; return (report, server, sleep, elapsed, left)."""
    sleep = FakeSleep()
    kwargs.setdefault("sleep", sleep)

    async def main():
        server = FakeServer(routes)
        transport = httpx.MockTransport(server.handler)
        async with httpx.AsyncClient(transport=transport) as client:
            start = time.perf_counter()
            async with asyncio.timeout(10):
                report = await download_all(client, urls, dest, **kwargs)
            elapsed = time.perf_counter() - start
        left = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        return report, server, elapsed, left

    report, server, elapsed, left = asyncio.run(main())
    return report, server, sleep, elapsed, left


def part_files(folder):
    return sorted(p.name for p in folder.rglob("*.part"))


# ---------------------------------------------------------------- file names

def test_file_name_is_last_path_segment():
    assert file_name("https://x.test/a/b/report.pdf") == "report.pdf", (
        "The file name is the last segment of the URL path."
    )
    assert file_name("https://x.test/img/cat.png?size=large#top") == "cat.png", (
        "Ignore the query string and fragment: use httpx.URL(url).path, not the raw string."
    )
    assert file_name("https://x.test/docs/") == "index.html", (
        "A path ending in '/' has an empty last segment: use 'index.html'."
    )
    assert file_name("https://x.test") == "index.html"


# ---------------------------------------------------------------- happy path

def test_downloads_exact_bytes(tmp_path):
    data = bytes(range(256)) * 10
    report, _, _, _, _ = download({"/data.bin": [ok(data)]}, [url("data.bin")], tmp_path)
    assert report == {url("data.bin"): "ok"}, f"Report was {report}."
    saved = tmp_path / "data.bin"
    assert saved.exists(), "The file must be saved as dest / file_name(url)."
    assert saved.read_bytes() == data, (
        "The saved bytes differ from the body. Write the raw bytes in binary mode ('wb'), not text."
    )
    assert part_files(tmp_path) == [], "The .part file must be renamed away after success."


def test_creates_missing_destination(tmp_path):
    dest = tmp_path / "new" / "folder"
    report, _, _, _, _ = download({"/a.txt": [ok(b"A")]}, [url("a.txt")], str(dest))
    assert report[url("a.txt")] == "ok"
    assert (dest / "a.txt").read_bytes() == b"A", (
        "dest may be a str and may not exist yet: Path(dest).mkdir(parents=True, exist_ok=True)."
    )


def test_report_keeps_input_order(tmp_path):
    routes = {"/slow.txt": [ok(b"s", delay=0.1)], "/fast.txt": [ok(b"f")], "/gone.txt": [status(404)]}
    urls = [url("slow.txt"), url("gone.txt"), url("fast.txt")]
    report, _, _, _, _ = download(routes, urls, tmp_path)
    assert list(report) == urls, (
        f"Report keys came out as {list(report)}. Keep the order of urls, not of completion."
    )
    assert report == {urls[0]: "ok", urls[1]: "failed: HTTP 404", urls[2]: "ok"}, f"Got {report}."


def test_empty_url_list(tmp_path):
    report, _, _, _, _ = download({}, [], tmp_path)
    assert report == {}, "No urls: return an empty dict."


# ---------------------------------------------------------------- limits

def test_never_more_than_limit_in_flight(tmp_path):
    names = [f"f{i}.txt" for i in range(10)]
    routes = {f"/{n}": [ok(n.encode(), delay=0.05)] for n in names}
    report, server, _, elapsed, _ = download(routes, [url(n) for n in names], tmp_path, limit=3)
    assert all(v == "ok" for v in report.values()), f"Report: {report}"
    assert server.peak <= 3, (
        f"{server.peak} requests were in flight at once with limit=3. Wrap each download in "
        "'async with semaphore' (one asyncio.Semaphore(limit) shared by all)."
    )
    assert server.peak == 3, (
        f"Peak was only {server.peak}: downloads are not running concurrently. Start one task "
        "per url (TaskGroup or gather) instead of awaiting them one by one."
    )
    assert elapsed < 0.4, f"10 downloads of 0.05s with limit 3 took {elapsed:.2f}s (serial: 0.5s)."


def test_limit_one(tmp_path):
    routes = {f"/f{i}": [ok(b"x", delay=0.01)] for i in range(4)}
    _, server, _, _, _ = download(routes, [url(f"f{i}") for i in range(4)], tmp_path, limit=1)
    assert server.peak == 1, "limit=1 means one download at a time."


def test_bad_limit(tmp_path):
    with pytest.raises(ValueError):
        download({}, [], tmp_path, limit=0)


# ---------------------------------------------------------------- retries

def test_retries_5xx_with_backoff(tmp_path):
    routes = {"/r.txt": [status(503), status(502), ok(b"finally")]}
    report, server, sleep, _, _ = download(routes, [url("r.txt")], tmp_path)
    assert report[url("r.txt")] == "ok", f"Got {report}. 5xx answers are temporary: retry them."
    assert server.calls["/r.txt"] == 3, f"Expected 3 attempts, the server saw {server.calls}."
    assert sleep.delays == pytest.approx([0.1, 0.2]), (
        f"Backoff delays were {sleep.delays}; expected [0.1, 0.2] (0.1 * 2**attempt), done "
        "with the injected sleep parameter, not asyncio.sleep."
    )
    assert (tmp_path / "r.txt").read_bytes() == b"finally"


def test_gives_up_after_retries(tmp_path):
    routes = {"/down.txt": [status(500)]}
    report, server, sleep, _, _ = download(routes, [url("down.txt")], tmp_path, retries=2)
    assert report[url("down.txt")] == "failed: HTTP 500", (
        f"Got {report[url('down.txt')]!r}; after the last attempt report 'failed: HTTP <code>'."
    )
    assert server.calls["/down.txt"] == 3, "retries=2 means 3 attempts in total."
    assert sleep.delays == pytest.approx([0.1, 0.2]), (
        f"Delays {sleep.delays}: sleep before each retry, never after the last attempt."
    )
    assert not (tmp_path / "down.txt").exists(), "A failed download must not leave a file."


def test_4xx_not_retried(tmp_path):
    routes = {"/secret.txt": [status(403), ok(b"no")]}
    report, server, sleep, _, _ = download(routes, [url("secret.txt")], tmp_path)
    assert report[url("secret.txt")] == "failed: HTTP 403", f"Got {report}."
    assert server.calls["/secret.txt"] == 1, "4xx is permanent: do not retry it."
    assert sleep.delays == []


def test_transport_errors_are_retried(tmp_path):
    routes = {"/net.txt": [network_error(httpx.ConnectError), ok(b"back")]}
    report, server, _, _, _ = download(routes, [url("net.txt")], tmp_path)
    assert report[url("net.txt")] == "ok", "httpx.TransportError (e.g. ConnectError) is temporary: retry."
    assert server.calls["/net.txt"] == 2


def test_transport_error_reason_is_the_type_name(tmp_path):
    routes = {"/net.txt": [network_error(httpx.ConnectError)]}
    report, server, _, _, _ = download(routes, [url("net.txt")], tmp_path, retries=1)
    assert report[url("net.txt")] == "failed: ConnectError", (
        f"Got {report[url('net.txt')]!r}; report 'failed: ' + type(error).__name__."
    )
    assert server.calls["/net.txt"] == 2


def test_one_failure_does_not_stop_the_others(tmp_path):
    routes = {"/bad.txt": [status(404)], "/good1.txt": [ok(b"1", 0.02)], "/good2.txt": [ok(b"2", 0.02)]}
    urls = [url("bad.txt"), url("good1.txt"), url("good2.txt")]
    report, _, _, _, _ = download(routes, urls, tmp_path)
    assert report == {urls[0]: "failed: HTTP 404", urls[1]: "ok", urls[2]: "ok"}, (
        f"Got {report}. Turn each failure into a report entry; do not let it cancel the others."
    )


# ---------------------------------------------------------------- partial files

def test_broken_body_leaves_no_files(tmp_path):
    routes = {"/big.bin": [broken_stream(b"half of it")]}
    report, server, _, _, _ = download(routes, [url("big.bin")], tmp_path, retries=1)
    assert report[url("big.bin")] == "failed: ReadError", f"Got {report}."
    assert server.calls["/big.bin"] == 2, "A broken body is a transport error: retry it."
    assert part_files(tmp_path) == [], (
        f"Left behind: {part_files(tmp_path)}. Delete the .part file whenever an attempt fails."
    )
    assert not (tmp_path / "big.bin").exists(), "A failed download must not leave the final file."


def test_retry_after_broken_body_starts_fresh(tmp_path):
    routes = {"/big.bin": [broken_stream(b"GARBAGE-"), ok(b"complete body")]}
    report, _, _, _, _ = download(routes, [url("big.bin")], tmp_path)
    assert report[url("big.bin")] == "ok"
    content = (tmp_path / "big.bin").read_bytes()
    assert content == b"complete body", (
        f"The file holds {content!r}. Each attempt must start from an empty file: open the "
        ".part file with 'wb' (not 'ab') and delete it when an attempt fails, or bytes from the "
        "failed attempt stay at the front."
    )


def test_final_name_appears_only_when_complete(tmp_path):
    seen_while_running = {}

    async def main():
        server = FakeServer({"/movie.mp4": [paused_stream(b"part one|", b"part two")]})
        async with httpx.AsyncClient(transport=httpx.MockTransport(server.handler)) as client:
            task = asyncio.create_task(download_all(client, [url("movie.mp4")], tmp_path))
            async with asyncio.timeout(3):
                while server.reached < 1 and not task.done():
                    await asyncio.sleep(0.01)
            seen_while_running["final"] = (tmp_path / "movie.mp4").exists()
            server.resume.set()
            async with asyncio.timeout(3):
                return await task

    report = asyncio.run(main())
    assert seen_while_running["final"] is False, (
        "movie.mp4 existed while the download was still running. Write to 'movie.mp4.part' and "
        "rename it (Path.replace) only after the last byte, so a reader never sees half a file."
    )
    assert report[url("movie.mp4")] == "ok"
    assert (tmp_path / "movie.mp4").read_bytes() == b"part one|part two"
    assert part_files(tmp_path) == []


# ---------------------------------------------------------------- timeouts

def test_slow_server_times_out(tmp_path):
    routes = {"/slow.txt": [slow(5.0)], "/quick.txt": [ok(b"q")]}
    urls = [url("slow.txt"), url("quick.txt")]
    report, server, sleep, elapsed, _ = download(routes, urls, tmp_path, timeout=0.15)
    assert report == {urls[0]: "timeout", urls[1]: "ok"}, (
        f"Got {report}. Wrap each attempt in 'async with asyncio.timeout(timeout)' and report "
        "'timeout' (httpx's own timeout setting is ignored by the fake transport)."
    )
    assert elapsed < 1.0, f"Took {elapsed:.2f}s; the slow download should be cut off at 0.15s."
    assert server.calls["/slow.txt"] == 1, "A timed-out download is reported, not retried."


def test_timeout_mid_body_removes_part_file(tmp_path):
    routes = {"/stuck.bin": [paused_stream(b"some bytes", b"never", wait_seconds=5.0)]}
    report, _, _, elapsed, _ = download(routes, [url("stuck.bin")], tmp_path, timeout=0.2)
    assert report[url("stuck.bin")] == "timeout", f"Got {report}."
    assert elapsed < 1.5
    assert part_files(tmp_path) == [], (
        f"Left behind: {part_files(tmp_path)}. A timeout arrives as a cancellation inside your "
        "code: clean up in 'finally' or 'except BaseException', not only 'except Exception'."
    )
    assert not (tmp_path / "stuck.bin").exists()


# ---------------------------------------------------------------- cancellation

def test_cancel_whole_download_cleans_up(tmp_path):
    state = {}

    async def main():
        routes = {
            "/done.txt": [ok(b"finished early")],
            "/big1.bin": [paused_stream(b"x" * 1000, b"y")],
            "/big2.bin": [paused_stream(b"x" * 1000, b"y")],
            "/big3.bin": [paused_stream(b"x" * 1000, b"y")],
        }
        server = FakeServer(routes)
        urls = [url("done.txt"), url("big1.bin"), url("big2.bin"), url("big3.bin")]
        async with httpx.AsyncClient(transport=httpx.MockTransport(server.handler)) as client:
            task = asyncio.create_task(download_all(client, urls, tmp_path, limit=2))
            async with asyncio.timeout(3):
                while server.reached < 2 and not task.done():   # two big downloads are mid-body
                    await asyncio.sleep(0.01)
            task.cancel()
            try:
                async with asyncio.timeout(3):
                    await task
            except asyncio.CancelledError:
                state["raised"] = "CancelledError"
            except TimeoutError:
                state["raised"] = "hang"
            state["cancelled"] = task.cancelled()
        state["left"] = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    asyncio.run(main())
    assert state.get("raised") == "CancelledError", (
        f"After task.cancel(), awaiting the download gave {state.get('raised')!r}. Let the "
        "CancelledError propagate: never swallow it in an 'except' or turn it into a report."
    )
    assert state["cancelled"], "task.cancelled() must be True after cancelling download_all."
    assert part_files(tmp_path) == [], (
        f"Left behind after cancel: {part_files(tmp_path)}. Remove the .part file when an "
        "attempt is cancelled (try/except BaseException or finally)."
    )
    assert not (tmp_path / "big1.bin").exists() and not (tmp_path / "big2.bin").exists(), (
        "Cancelled downloads must not leave a final file."
    )
    assert (tmp_path / "done.txt").read_bytes() == b"finished early", (
        "Files that were completely downloaded before the cancel should stay."
    )
    assert state["left"] == [], (
        f"{len(state['left'])} task(s) kept running after the cancel. Use a TaskGroup (or "
        "cancel and await your tasks) so cancelling download_all stops every download."
    )


def test_no_tasks_left_after_return(tmp_path):
    routes = {"/a": [ok(b"a")], "/b": [status(500)], "/c": [slow(5.0)]}
    _, _, _, _, left = download(routes, [url("a"), url("b"), url("c")], tmp_path, timeout=0.1)
    assert left == [], f"{len(left)} task(s) still alive after download_all returned."
