# Data and fixtures for problems

Problems must work **offline, small, and the same on every machine**. This guide says where a problem's data
comes from and how to make it. Companion to [problem-writing-library-tracks.md](problem-writing-library-tracks.md).

## What reaches the learner

- `learn start` gives the learner `starter.py` (as `solution.py`) and `problem.md` only.
- `learn check` copies the learner's `.py .txt .csv .json .md .toml .yaml .yml` files, then `test_solution.py`,
  `conftest.py` and the whole `fixtures/` folder into a temporary folder. `.xlsx .ipynb .sql .parquet .png .pdf` in the
  learner's folder are **not** copied.
- So: the **test** reads fixtures and passes data to the solution as arguments. The solution never opens a fixture.
  A file the solution must write goes to a path the test passes in (`tmp_path`).

## Choose the source (in this order)

| Need | Use | Why |
|---|---|---|
| a few rows | inline in the test (`pd.DataFrame({...})`, a list) | readable, hand-checkable |
| larger data with a known truth | a **generator** function in `conftest.py` with a seed | tests can say "recovers the true value" |
| a real small dataset | a file in `fixtures/` (CSV/JSON/NPZ, under ~100 KB) | stable, reviewable |
| files the solution must read from disk | the test **writes them** into `tmp_path` and passes the path | no fixture path leaks into the solution |
| a PDF, image, or workbook | the test generates it (`minipdf.make_pdf`, Pillow, openpyxl) into `tmp_path` | the format is not copied otherwise |
| a pretrained model | the test **trains** a tiny one in under a second, or builds it from a config | never download a model |

Never: a network call, `load_dataset("name")`, `from_pretrained("name")`, a path outside the problem, a file over about
1 MB, data scraped from a site whose licence you did not read.

## Generators with a known truth

Write the true model in the docstring and **copy the chapter's generator verbatim** so numbers match the chapter.

```python
def make_clicks(n, seed, lift=0.02, base=0.10):
    """Two groups. True click rate: base for A, base + lift for B."""
    rng = np.random.default_rng(seed)
    group = rng.integers(0, 2, n)
    clicked = rng.random(n) < (base + lift * group)
    return pd.DataFrame({"group": np.where(group == 1, "B", "A"), "clicked": clicked})
```

Rules:

- A `seed` argument always; the solution receives the generated data, not the seed (unless randomness is the topic).
- NumPy does not promise the same stream across versions. So **do not** hard-code a number computed from the
  generated data. Compute the expected value in the test from the same data with an obvious method, or
  compare with the true parameter within a margin that holds on 3 seeds.
- Keep n small enough that the test file stays near 20 s total.

## Fixture files

| Format | Notes |
|---|---|
| CSV | `encoding="utf-8"`, `newline=""` when written by Python; header row; no index column; LF line ends |
| JSON | UTF-8, sorted keys if the order matters |
| NPZ | `np.savez_compressed`; load with `np.load` in the **test**; keep dtypes small (`uint8`, `float32`) |
| Parquet | needs `pyarrow`; fine as a fixture, but it is not copied from the learner's folder, so only the test reads it |

Put a short `fixtures/README.md` in any problem or module that ships a data file: where it came from, the licence,
how it was made (the command), its size. If it is derived, the command must reproduce it.

### Recipe: the digits set without sklearn (ml tracks; M3)

torch tests cannot import sklearn (address-space cap), so ship the data once.

```bash
python - <<'EOF'
import numpy as np
from sklearn.datasets import load_digits
d = load_digits()
np.savez_compressed("fixtures/digits.npz", X=d.data.astype(np.uint8), y=d.target.astype(np.uint8))
EOF
```

Result checked 2026-11-25: `X` shape `(1797, 64)`, dtype `uint8`, max 16; file about 45 KB. In the test:
`z = np.load(Path(__file__).parent / "fixtures" / "digits.npz")`, then pass tensors to the solution. The same data
is public (UCI optical recognition of handwritten digits); check the licence line on its UCI page before you add
it to the public `master` branch, and record it in `fixtures/README.md`.

### Where fixtures live

`content/<track>/<module>/problems/pNNN-slug/fixtures/` for one problem. If several problems of a module share a
file, copy it into each (the runner copies only that problem's folder) or generate it in a `conftest.py` helper.
Do not rely on a shared folder outside the problem.

## Public datasets in capstones (not in problems)

Capstone data may be larger and real, but only public and legally reusable data. Download once, record the URL, date,
licence and SHA-256 checksum in `DATA.md`, keep raw files read-only, and work offline from the local copy. Capstones
live outside `my-work/` and the course repo (see the capstone guides). Never personal data about real people,
never company data.

## Checklist before a problem ships its data

- [ ] No fixture path or course helper import appears in `starter.py`, `reference.py` or `problem.md`'s solution code.
- [ ] Data are small (rows <= 5,000; images <= 32x32; files well under 1 MB).
- [ ] A seed everywhere; expected values do not depend on the random stream.
- [ ] Source and licence recorded for any real data; no personal information.
- [ ] A file the solution writes goes to a path passed in by the test.
- [ ] The test file still runs in about 20 s under `ulimit -v 1048576`.
