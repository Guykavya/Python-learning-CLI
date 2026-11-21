## Approach

The model answer is in `answer.md`. Each problem gets the same treatment: **situation, consequence, fix**. "It is bad style" is not an answer; "under cron the working directory is your home, so `pdfs/` is created there" is.

The five most damaging problems in practice are the silent ones: exit code 0 on failure (nobody notices), `print` for errors (nobody sees), and a relative destination (files go somewhere unexpected). Each of them turns a failure into something that looks like success.

## Cost

Reading only. The fixed version is longer (about 40 lines instead of 10), but each extra line removes one way to lose files or hide a failure.

## Another way

Rewrite the script yourself with the skeleton of section 2.2 and test it with `tmp_path` (chapter 4): a test that the dry run changes nothing, one that a missing folder returns 1, and one that nothing is overwritten. The tests are the proof that each problem is gone.
