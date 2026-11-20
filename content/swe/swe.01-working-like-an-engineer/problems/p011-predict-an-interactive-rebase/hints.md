## Hint 1

Read the list line by line and keep a short list of **result commits**. Start with `pick A`: the result is `[A]`.

## Hint 2

`reword B` adds a new result commit `B` with the subject `Add login form`. `fixup C` does not add a commit: it merges `C`'s changes into the last result commit (`B`) and throws `C`'s message away.

## Hint 3

`pick E` adds a result commit `E` (subject `Add docs`). `squash D` melds `D` into the last result commit, which is `E`, not into anything related by name: squash always goes into the commit **above it in the list**. Its subject stays `Add docs`. `drop F` removes `F`.
