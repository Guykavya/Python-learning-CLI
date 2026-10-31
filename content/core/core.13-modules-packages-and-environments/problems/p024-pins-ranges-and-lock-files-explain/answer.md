**1. Ranges and pins.** A range like `requests>=2.28,<3` says "any version from 2.28 up to, but not
including, 3.0 works with my code". It leaves room: the installer can pick a newer bug-fix release.
A pin like `requests==2.31.0` says "exactly this version". A pin gives the same result every time; a
range gives flexibility.

**2. Why the app broke.** `flask` and `tinytables` have their own dependencies, and those have more:
these are **transitive dependencies**. Team B listed only the two top names, without versions. On
every install the **resolver** (pip, uv or poetry) chooses the newest versions that satisfy all ranges
it sees. On Wednesday one transitive package released a breaking version that still fit the ranges,
so Thursday's install picked it. The code was the same; the installed set of packages was not.

**3. Libraries use ranges.** A library is installed *next to* other libraries in someone else's
environment. If `tinytables` pinned `requests==2.31.0` and another library pinned
`requests==2.30.0`, the resolver could not satisfy both, and the user could not install the two
together at all ("ResolutionImpossible"). It would also block security fixes. A library should state
the widest range it really supports: a lower bound it was tested with, and an upper bound only when a
known break exists (`<3`).

**4. Lock files.** A lock file is the exact result of one resolution: every package in the
environment, transitive ones included, with an exact version and often a hash of the file, so a
changed or fake download is refused. `uv lock` writes `uv.lock`, poetry writes `poetry.lock`, and
`pip freeze > requirements.txt` (or `pip-compile`) gives a pinned list. Installing from the lock file
(`uv sync`, `pip install -r requirements.txt`) rebuilds the same environment on Monday, Thursday and on
the server. That is what Team B was missing.

**5. Together.** `pyproject.toml` keeps ranges: what the code *can* work with. The lock file is
committed for an application: what was *tested*. To upgrade on purpose you run the resolver again
(`uv lock --upgrade`, `poetry update`, or a fresh `pip-compile`), run the tests, and commit the new
lock file. So Rohan is right for the app's lock file, wrong for `tinytables`.
