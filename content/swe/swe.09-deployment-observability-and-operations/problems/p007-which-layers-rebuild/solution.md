## Approach

| Edit | Earliest step it changes | Steps rebuilt |
|---|---|---|
| `app/main.py` edited | 6: `COPY app ./app` copies that file | 6, 7, 8, 9 -> **4** |
| `requirements.txt` edited | 4: `COPY requirements.txt .` | 4 to 9 -> **6** (including the slow `pip install`, step 5) |
| base image tag changed | 1: `FROM python:3.13-slim` | 1 to 9 -> **9** |
| `CMD` line edited | 9: the last step | **1** |
| `README.md` edited | none: no `COPY` copies it | **0**: every step is cached |

The order of the Dockerfile follows the rule "things that change rarely come first": the base image, the user, the dependencies; the code, which changes with almost every commit, comes last, so a code change rebuilds only 4 cheap steps and never the `pip install`.

## Cost

Reading only. In real life the difference is the build time: the chapter's captured builds show the cached steps reused and only the copy of the code rebuilt, instead of a full reinstall of every dependency.

## Another way

Run the program, then try the wrong order: swap lines 4 to 6 so that `COPY app ./app` comes first, and see how a one-line code edit now rebuilds the `pip install` (this is the problem of `COPY . .` before `RUN pip install`, which p006 detects).
