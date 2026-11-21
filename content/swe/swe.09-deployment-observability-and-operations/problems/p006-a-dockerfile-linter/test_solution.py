import pytest

from solution import lint_dockerfile

CHAPTER = '''# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN useradd --create-home --uid 10001 app
WORKDIR /srv

# dependencies first: this layer is rebuilt only when requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# application code last: it changes most often
COPY app ./app

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \\
    DATABASE_PATH=/data/pagebound.db
RUN mkdir /data && chown app:app /data
VOLUME /data

USER app
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=3 \\
    CMD ["python", "-c", "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=1).status == 200 else 1)"]

# exec form: uvicorn is PID 1 and receives SIGTERM directly
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
'''

SLOW = '''FROM python:3.14-slim
COPY . /srv
WORKDIR /srv
RUN pip install -r requirements.txt
CMD python -m uvicorn app.main:create_app --factory --host 0.0.0.0
'''


def test_the_chapter_dockerfile_is_clean():
    assert lint_dockerfile(CHAPTER) == [], \
        "The chapter's Dockerfile (section 5.2) follows every rule: expected []. Check line joining, ENV with several NAME=value pairs, and 'COPY requirements.txt .'."


def test_the_slow_dockerfile_of_the_chapter():
    assert lint_dockerfile(SLOW) == [(0, "no-user"), (2, "copy-before-install"), (5, "shell-cmd")], \
        "The chapter's 'why is this Dockerfile slow?' file: no USER (line 0), COPY . before pip install (line 2), shell-form CMD (line 5)."


@pytest.mark.parametrize("from_line, expected", [
    ("FROM python", [(1, "unpinned-base")]),
    ("FROM python:latest", [(1, "unpinned-base")]),
    ("FROM ghcr.io/me/app:latest", [(1, "unpinned-base")]),
    ("FROM python:3.14-slim", []),
    ("FROM localhost:5000/team/app:1.2", []),
    ("FROM localhost:5000/team/app", [(1, "unpinned-base")]),
    ("FROM python@sha256:" + "a" * 64, []),
    ("FROM scratch", []),
    ("FROM --platform=linux/amd64 python:3.14 AS runtime", []),
    ("FROM --platform=linux/amd64 python AS runtime", [(1, "unpinned-base")]),
    ("FROM ${BASE_IMAGE}", []),
    ("from python:3.14", []),
])
def test_unpinned_base(from_line, expected):
    got = [f for f in lint_dockerfile(from_line + "\nUSER app\n") if f[1] == "unpinned-base"]
    assert got == expected, f"{from_line!r}: expected {expected}, got {got}. A tag (other than latest), a digest, scratch and build arguments are fine."


def test_stage_reference_is_not_a_base_image():
    text = "FROM python:3.14-slim AS build\nRUN true\nFROM build\nUSER app\n"
    assert lint_dockerfile(text) == [], "FROM build refers to the stage named 'build'; it is not an untagged image."


def test_shell_and_exec_forms():
    base = "FROM python:3.14\nUSER app\n"
    assert lint_dockerfile(base + 'CMD ["python", "app.py"]\n') == [], "Exec form (a JSON list) is fine."
    assert lint_dockerfile(base + "CMD python app.py\n") == [(3, "shell-cmd")], "Shell form CMD: finding at its line."
    assert lint_dockerfile(base + "ENTRYPOINT /run.sh\n") == [(3, "shell-cmd")], "ENTRYPOINT in shell form is the same problem."
    assert lint_dockerfile(base + 'ENTRYPOINT ["/run.sh"]\n') == []
    assert lint_dockerfile(base + "cmd python app.py\n") == [(3, "shell-cmd")], "Instruction names are case-insensitive."


def test_copy_before_install():
    ok = "FROM python:3.14\nUSER app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\n"
    assert lint_dockerfile(ok) == [], "COPY . . AFTER the install is the right order."
    bad = "FROM python:3.14\nUSER app\nCOPY . .\nRUN pip install -r requirements.txt\n"
    assert lint_dockerfile(bad) == [(3, "copy-before-install")], "COPY . . before pip install: report the COPY line."
    assert lint_dockerfile("FROM python:3.14\nUSER app\nADD ./ /srv\nRUN pip install -r r.txt\n") == [(3, "copy-before-install")], \
        "ADD works like COPY; './' is the whole context too."
    assert lint_dockerfile("FROM python:3.14\nUSER app\nCOPY . .\nRUN echo hi\n") == [], "No pip install at all: nothing to compare with."
    assert lint_dockerfile("FROM python:3.14\nUSER app\nCOPY app ./app\nRUN pip install x\n") == [], "COPY app is not the whole context."


def test_copy_from_another_stage_is_not_the_context():
    text = "FROM python:3.14 AS build\nRUN pip wheel x\nFROM python:3.14\nUSER app\nCOPY --from=build . /srv\nRUN pip install y\n"
    assert lint_dockerfile(text) == [], "COPY --from=... copies from another stage, not from the build context."


def test_user_rules():
    assert lint_dockerfile("FROM python:3.14\n") == [(0, "no-user")], "No USER at all: finding on line 0."
    assert lint_dockerfile("FROM python:3.14\nUSER root\n") == [(0, "no-user")], "USER root is still root."
    assert lint_dockerfile("FROM python:3.14\nUSER 0:0\n") == [(0, "no-user")], "0 is root."
    assert lint_dockerfile("FROM python:3.14\nUSER root\nUSER app\n") == [], "Only the LAST USER counts."
    assert lint_dockerfile("FROM python:3.14\nUSER app\nUSER root\n") == [(0, "no-user")], "Ending as root is bad even after an earlier USER app."
    assert lint_dockerfile("FROM python:3.14\nUSER 10001\n") == [], "A numeric non-root user is fine."


def test_user_is_judged_in_the_last_stage():
    text = "FROM python:3.14 AS build\nUSER app\nFROM python:3.14\nRUN true\n"
    assert lint_dockerfile(text) == [(0, "no-user")], "The USER of the first stage does not protect the final image."


@pytest.mark.parametrize("line, hit", [
    ("ENV STRIPE_KEY=sk_live_abc", True),
    ("ENV APP_SECRET_KEY=abc", True),
    ("ENV DB_PASSWORD=hunter2", True),
    ("ARG API_TOKEN=abc", True),
    ("ENV TOKEN abc123", True),
    ("ENV AWS_API_KEY=abc", True),
    ("ENV PYTHONUNBUFFERED=1 SECRET_KEY=abc", True),
    ("ENV APP_SECRET_KEY=${APP_SECRET_KEY}", False),
    ("ENV APP_SECRET_KEY=", False),
    ("ARG API_TOKEN", False),
    ("ENV APP_VERSION=1.0", False),
    ("ENV KEYBOARD=us", False),
    ("ENV DATABASE_PATH=/data/db", False),
])
def test_secret_in_env(line, hit):
    got = [f for f in lint_dockerfile("FROM python:3.14\nUSER app\n" + line + "\n") if f[1] == "secret-in-env"]
    assert got == ([(3, "secret-in-env")] if hit else []), f"{line!r}: secret-in-env expected={hit}, got {got}"


def test_continuation_is_one_instruction_reported_at_its_first_line():
    text = "FROM python:3.14\nUSER app\nENV PYTHONUNBUFFERED=1 \\\n    API_TOKEN=abc \\\n    X=1\nCMD python x\n"
    assert lint_dockerfile(text) == [(3, "secret-in-env"), (6, "shell-cmd")], \
        "A secret on a continuation line is reported at the line where the ENV instruction starts, and line numbers go on counting."


def test_apt_cleanup():
    base = "FROM python:3.14\nUSER app\n"
    bad = base + "RUN apt-get update && apt-get install -y curl\n"
    assert lint_dockerfile(bad) == [(3, "apt-no-cleanup")], "apt-get install without removing the package lists."
    good = base + "RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*\n"
    assert lint_dockerfile(good) == []
    split = base + "RUN apt-get update \\\n && apt-get install -y curl \\\n && rm -rf /var/lib/apt/lists/*\n"
    assert lint_dockerfile(split) == [], "The cleanup on a continuation line belongs to the same RUN."


def test_several_findings_are_sorted():
    text = "FROM python\nENV SECRET_KEY=abc\nCOPY . .\nRUN pip install x\nCMD run\n"
    assert lint_dockerfile(text) == [(0, "no-user"), (1, "unpinned-base"), (2, "secret-in-env"), (3, "copy-before-install"), (5, "shell-cmd")], \
        "Sort by line number, then code; the whole-file finding (line 0) comes first."


def test_comments_and_blank_lines_are_ignored():
    text = "# CMD python x\n\nFROM python:3.14\n# USER root\nUSER app\n"
    assert lint_dockerfile(text) == [], "Commented-out instructions must not count."
