"""statsmodels loads OpenBLAS with one thread pool per core; under the 1 GiB test cap one thread is enough
and saves about 80 MB of address space. Must run before numpy is imported."""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
